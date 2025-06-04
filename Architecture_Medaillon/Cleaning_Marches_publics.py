from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, explode
from pyspark.sql.types import DoubleType

# ---------------------------------------------------
# 1. SparkSession
# ---------------------------------------------------
spark = SparkSession.builder.appName("CleanMarchesPublics2022").getOrCreate()

# ---------------------------------------------------
# 2. Lecture du fichier JSON brut
# ---------------------------------------------------
df_raw = spark.read.option("multiline", "true").json("/opt/bitnami/spark/Architecture_Medaillon/bronze/Marches_publics.json")

# Extraire le tableau "marches"
df = df_raw.selectExpr("explode(marches) as marche").select("marche.*")

# ---------------------------------------------------
# 3. Nettoyage + flatten acheteur / lieu
# ---------------------------------------------------
df = df.select(
    "id", "uid", "nature", "objet", "codeCPV", "procedure", "dureeMois",
    "dateNotification", "montant", "formePrix",
    col("acheteur.id").alias("acheteur_id"),
    col("acheteur.nom").alias("acheteur_nom"),
    col("lieuExecution.code").alias("lieu_code"),
    col("lieuExecution.nom").alias("lieu_nom"),
    col("titulaires").alias("titulaires")
)

# ---------------------------------------------------
# 4. Une ligne par titulaire
# ---------------------------------------------------
df = df.withColumn("titulaire", explode("titulaires"))
df = df.withColumn("titulaire_siret", col("titulaire.id"))
df = df.withColumn("titulaire_nom", col("titulaire.denominationSociale"))
df = df.drop("titulaire", "titulaires")

# ---------------------------------------------------
# 5. Nettoyage types
# ---------------------------------------------------
df = df.withColumn("montant", col("montant").cast(DoubleType()))
df = df.withColumn("dateNotification", to_date("dateNotification"))

# ---------------------------------------------------
# 6. Sauvegarde en JSON (1 ligne = 1 marché × 1 titulaire)
# ---------------------------------------------------
df.coalesce(1).write.mode("overwrite").json("/opt/bitnami/spark/Architecture_Medaillon/silver/Marches_publics_cleaned.json")