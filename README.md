# XCNV-Lambda

## 1 - Presentation

This project is an implementation of XCNV (https://github.com/kbvstmd/XCNV) to an AWS Lambda image. It is used at https://sars-engine.com/CNV/ to compare score to AChro-Puce, ACMG-Franklin and CNV-Hub computed scores.

## 2 - Configuring AWS S3

The project is designed to upload results in S3 bucket. Add your S3 credentials in cloud/credentials.config (copy the template file cloud/credentials_example.cloud and rename it). The results will be stored in /xcnv folder in your S3 bucket.


## 3 - Configuring AWS Lambda

Once you have uploaded the image to your AWS Elastic Container Registry (ECR), you can use it in AWS Lambda. The image requires 2 GB of ephemere storage, 6-7 GB of RAM and 5-7 minutes timeout (the firsts run are very slow in AWS Lambda).

The image receive queries in ["headers"]["queries"] as a tab separeted comma (.tsv) string which represents a 4 columns table.

Columns :
- Chromosome ( 1 to 22 or X or Y )
- Start
- End
- Variation type ( gain or loss )

Example with 1 query :
````
1  1000000 2000000 gain
````

Your Test event/Test JSON will looks like :
````
{
  "headers": {
    "queries": "1  1000000 2000000 gain",
  }
}
````

Example with 2 query :
````
1  1000000 2000000 gain
1  1000000 2000000 loss
````

To write several query in one string, use the '\n' character such as :
````
1  1000000 2000000 gain\n1  1000000 2000000 loss
````

Your Test event/Test JSON will looks like :
````
{
  "headers": {
    "queries": "1  1000000 2000000 gain\n1  1000000 2000000 loss",
  }
}
````

## 4 - Local Usage 

You can directly use https://github.com/kbvstmd/XCNV or install XCNV by unzipping XCNV.tar.gz. Then follow the installation instructions given at https://github.com/kbvstmd/XCNV.
And then, collect the results which are in xcnv_data in xcnv_lambda.py.
