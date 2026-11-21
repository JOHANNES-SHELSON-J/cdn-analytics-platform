import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame

def sparkSqlQuery(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node AWS Glue Data Catalog
AWSGlueDataCatalog_node1784156767966 = glueContext.create_dynamic_frame.from_catalog(database="cdn_analytics_db", table_name="raw", transformation_ctx="AWSGlueDataCatalog_node1784156767966")

# Script generated for node SQL Query
SqlQuery1091 = '''
SELECT * FROM myDataSource WHERE latency_ms IS NOT NULL
'''
SQLQuery_node1784157057333 = sparkSqlQuery(glueContext, query = SqlQuery1091, mapping = {"myDataSource":AWSGlueDataCatalog_node1784156767966}, transformation_ctx = "SQLQuery_node1784157057333")

# Script generated for node Change Schema
ChangeSchema_node1784157158350 = ApplyMapping.apply(frame=SQLQuery_node1784157057333, mappings=[("timestamp", "string", "timestamp", "timestamp"), ("region", "string", "region", "string"), ("customer_id", "string", "customer_id", "string"), ("status_code", "long", "status_code", "long"), ("latency_ms", "double", "latency_ms", "double"), ("cache_status", "string", "cache_status", "string"), ("bytes_sent", "long", "bytes_sent", "long"), ("year", "string", "year", "string"), ("month", "string", "month", "string"), ("day", "string", "day", "string")], transformation_ctx="ChangeSchema_node1784157158350")

# Script generated for node Amazon S3
AmazonS3_node1784157217000 = glueContext.getSink(path="s3://cdn-analytics-joey-2026/curated/", connection_type="s3", updateBehavior="UPDATE_IN_DATABASE", partitionKeys=["year", "month", "day"], enableUpdateCatalog=True, transformation_ctx="AmazonS3_node1784157217000")
AmazonS3_node1784157217000.setCatalogInfo(catalogDatabase="cdn_analytics_db",catalogTableName="curated")
AmazonS3_node1784157217000.setFormat("glueparquet", compression="snappy")
AmazonS3_node1784157217000.writeFrame(ChangeSchema_node1784157158350)
job.commit()