# XCNV-Lambda

## 1 - Presentation and Usage

This project is an implementation of XCNV (https://github.com/kbvstmd/XCNV) to an AWS Lambda image. The image receive queries in ["headers"]["queries"] as a tab separeted comma (.tsv) string which represents a 4 columns table.

Columns :
- Chromosome ( 1 to 22 or X or Y )
- Start
- End
- Variation type ( gain or loss )

Example with 1 query :
````
1  1000000 2000000 gain
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

## 2 - Using AWS S3

The project is designed to upload result in S3 bucket. Add your S3 credentials in cloud/credentials.config (copy the template file cloud/credentials_example.cloud and rename it)

## 3 - Local Usage 

You can directly use https://github.com/kbvstmd/XCNV or install XCNV by unzipping XCNV.tar.gz. Then follow the installation instructions given at https://github.com/kbvstmd/XCNV.
And then, collect the results which are in xcnv_data in xcnv_lambda.py.
