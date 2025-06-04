from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim
from pyspark.sql.types import StringType
 
# Initialiser Spark
spark = SparkSession.builder.appName("CleanEtablissements").getOrCreate()
 
# Charger les données
df = spark.read.option("header", "true").csv("bronze/simulated_etablissements_50000.csv")
 
# Calcul du seuil de colonnes à conserver (>10% de données non nulles)
row_count = df.count()
threshold = row_count * 0.1
 
# Conserver les colonnes avec suffisamment de valeurs non nulles
non_null_counts = df.select([
    col(c).isNotNull().cast("int").alias(c) for c in df.columns
]).groupBy().sum().collect()[0].asDict()
columns_to_keep = [c.replace("sum(", "").replace(")", "") for c, v in non_null_counts.items() if v >= threshold]
df_cleaned = df.select(columns_to_keep)
 
# Supprimer les doublons sur la colonne 'siret'
df_cleaned = df_cleaned.dropDuplicates(["siret"])
 
# Nettoyer les chaînes : trim (enlever les espaces)
for column in df_cleaned.columns:
    df_cleaned = df_cleaned.withColumn(column, trim(col(column).cast(StringType())))
 
# Garder uniquement les établissements actifs
df_cleaned = df_cleaned.filter(col("etatAdministratifEtablissement") == "A")
 
# Sauvegarder dans silver
df_cleaned.write.mode("overwrite").option("header", "true").csv("silver/simulated_etablissements_50000.csv")