from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year

# ---------------------------------------------------
# 1. Initialiser Spark
# ---------------------------------------------------
spark = SparkSession.builder.appName("MergeMarchesEtablissements").getOrCreate()

# ---------------------------------------------------
# 2. Charger les datasets cleans
# ---------------------------------------------------
marches = spark.read.json("/opt/bitnami/spark/Architecture_Medaillon/silver/Marches_publics_cleaned.json")
etabs = spark.read.option("header", "true").csv("/opt/bitnami/spark/Architecture_Medaillon/silver/Etablissement_information_cleaned.csv")

# ---------------------------------------------------
# 3. Jointure sur le SIRET
# ---------------------------------------------------
df = marches.join(etabs, marches.titulaire_siret == etabs.siret, how="inner")

# ---------------------------------------------------
# 4. Filtrer : marchés notifiés en 2022
# ---------------------------------------------------
df = df.filter(year(col("dateNotification")) == 2022)

# ---------------------------------------------------
# 5. Colonnes à garder
# ---------------------------------------------------
df_final = df.select(
    "id", "nature", "objet", "montant", "dateNotification",
    "titulaire_siret", "titulaire_nom",
    "acheteur_id", "acheteur_nom",
    "lieu_code", "lieu_nom"
)

# ---------------------------------------------------
# 6. Sauvegarde au format CSV (gold)
# ---------------------------------------------------
df_final.coalesce(1).write.mode("overwrite").option("header", "true").csv(
    "/opt/bitnami/spark/Architecture_Medaillon/gold/marches_2022_etabs_actifs.csv"
)

print("✅ Fusion réussie : marchés 2022 + établissements actifs → gold/marches_2022_etabs_actifs.csv")
