from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator

spark = SparkSession.builder \
    .appName("ALS") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()

ratings_path = "/home/sunbeam/Desktop/movies/rating.csv"
movies_path = "/home/sunbeam/Desktop/movies/movie.csv"

ratings_df = spark.read.csv(ratings_path, header=True, inferSchema=True)
movies_df = spark.read.csv(movies_path, header=True, inferSchema=True)

print("Ratings Data:")
ratings_df.printSchema()

print("Movies Data:")
movies_df.printSchema()

(training_data, test_data) = ratings_df.randomSplit([0.8, 0.2], seed=42)

als = ALS(
    maxIter=10,
    regParam=0.1,
    userCol="userId",
    itemCol="movieId",
    ratingCol="rating",
    coldStartStrategy="drop"
)

als_model = als.fit(training_data)

predictions = als_model.transform(test_data)

evaluator = RegressionEvaluator(
    metricName="rmse",
    labelCol="rating",
    predictionCol="prediction"
)
rmse = evaluator.evaluate(predictions)
print(f"Root Mean Square Error (RMSE): {rmse:.4f}")

user_recommendations = als_model.recommendForAllUsers(10)

movie_recommendations = als_model.recommendForAllItems(10)

user_id = int(input("Enter UserId to Recommend him Top 10 Movies :: "))
single_user_recs = (
    user_recommendations.filter(col("userId") == user_id)
    .select("recommendations")
    .rdd.flatMap(lambda x: x[0])
    .collect()
)

print(f"Top 10 recommendations for user {user_id}:")
for rec in single_user_recs:
    movie_id = rec[0]
    movie_rating = rec[1]
    movie_title = movies_df.filter(movies_df.movieId == movie_id).select("title").collect()[0]["title"]
    print(f"Movie: {movie_title}, Predicted Rating: {movie_rating:.2f}")

spark.stop()
