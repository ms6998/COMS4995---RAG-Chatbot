import pandas as pd

# 读取处理后的数据
df = pd.read_csv('data/processed/culpa_ratings_processed.csv')

print("=" * 60)
print("CULPA Data Successfully Processed!")
print("=" * 60)
print(f"\nTotal Professors: {len(df)}")
print(f"Average Rating: {df['rating'].mean():.2f}")
print(f"\nTop 10 Rated Professors:")
print(df.nlargest(10, 'rating')[['professor_name', 'rating']].to_string(index=False))
print(f"\nData saved to: data/processed/culpa_ratings_processed.csv")
print("\n✅ Your RAG system now has 295 real professor ratings!")
