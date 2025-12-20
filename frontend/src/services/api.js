const BASE_URL = "https://pathwise-1056631112792.us-east1.run.app";

/**
 * IMPORTANT: Tokens expire every 60 minutes.
 * Run 'gcloud auth print-identity-token' and paste below.
 */
const AUTH_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjZhOTA2ZWMxMTlkN2JhNDZhNmE0M2VmMWVhODQyZTM0YThlZTA4YjQiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIzMjU1NTk0MDU1OS5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsImF1ZCI6IjMyNTU1OTQwNTU5LmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwic3ViIjoiMTEzODk0MDc1NTUxNDQ4OTkwNDI3IiwiaGQiOiJjb2x1bWJpYS5lZHUiLCJlbWFpbCI6ImJrMjgzM0Bjb2x1bWJpYS5lZHUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6Ijc4V3FOQlg0Nkl5WFN0T1pGc0c5anciLCJpYXQiOjE3NjYyMDAxOTIsImV4cCI6MTc2NjIwMzc5Mn0.yVmUm0CVSeeo7MGiKMQSazMUoMyZ3B-0TihQMKDHCuym9-KJTzqlZSMwe5N3jkL4wI3SwPRX_xLMkAj7k97ALvNy-w4WwFLytQl-rE4NKng32IEv7EAkRMkez27Iue6MRhYtbIWTdbgmpxCUEQMCCqkslvO_VXaXbNzSu_WzvEmIpSREV3noeDvuzBYnF2YSZ1thm2L7pEU4yHIDx3vo0vrG9J4ISINjanfn5IziiVNpzPni6B4tjXwXLR686RyOy5R6kVtVVN0FMC8aydn-DCpkNPbtpmv0DXWHqQY2isLlIuUko2BBbBufYyPsovYE-qkbIIzXNzaWP_JbFQUNng"; 

export const sendMessage = async (message, userMajor, endpoint = 'ask') => {
  const path = endpoint === 'professors' ? '/professors' : '/ask';
  
  // 1. Format course codes for professor rating lookups
  const match = message.match(/([a-zA-Z]{4})\s?([a-zA-Z]{0,2})\s?(\d{4})/i);
  let courseCodes = [];
  if (match) {
    const dept = match[1].toUpperCase();
    const num = match[3];
    const formattedCode = dept === "STAT" ? `STAT GR${num}` : 
                          dept === "IEOR" ? `IEOR E${num}` : `${dept} W${num}`;
    courseCodes = [formattedCode];
  }

  // 2. DYNAMIC GROUNDING: Uses userMajor instead of hardcoded "Computer Science"
  // This allows the RAG system to pull Civil Engineering docs when appropriate.
  //const groundedQuestion = `Based EXCLUSIVELY on the ${userMajor} 2023 Catalog and official degree requirements provided in your documents: ${message}`;
  const groundedQuestion = endpoint === 'plan' 
  ? `Create a 3-semester table for MS in CS (30 credits) using the 2023 requirements. 
     Columns: Semester, Course, Category. 
     Include 4 cores and 6 electives. 
     No introduction, no disclaimer, no list of all options. Just the table.`
  : `Based EXCLUSIVELY on the ${userMajor} 2023 Catalog: ${message}`;

  const payload = {
    question: groundedQuestion,
    user_profile: { 
        program: userMajor, 
        level: "Graduate", 
        start_year: 2025, 
        catalog_year: 2023 
    },
    generation_config: {
        max_output_tokens: 3000, 
        temperature: 0.2
    }
  };

  if (endpoint === 'professors') {
    payload.course_codes = courseCodes;
  }

  try {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${AUTH_TOKEN}`
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`API Error: ${response.status}`);
    
    const data = await response.json();

    // 3. Format Professor Response
    if (endpoint === 'professors' && data.professors) {
      const code = Object.keys(data.professors)[0];
      const profs = data.professors[code];

      if (!profs || profs.length === 0) {
        return `I couldn't find ratings for **${code}** in the professor database.`;
      }

      let result = `### Recommendations for ${code}:\n`;
      profs.forEach(p => {
        result += `* **${p.prof_name}**: ⭐ ${p.rating.toFixed(1)}/5.0\n`;
      });
      return result;
    }

    // 4. Return standard answer
    // Backend returns data.answer for /ask and data.explanation for /plan
    return data.answer || data.explanation || "No data retrieved.";
    
  } catch (error) {
    console.error("Fetch Error:", error);
    throw error;
  }
};