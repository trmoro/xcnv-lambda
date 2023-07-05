import os
import csv
import json
import sys

from cloud.aws import getS3, setFile

#Convert Row to XCNV object
def row2xcnv(row):
	
	var_type = "loss"
	if int(row["Type"]) == 1:
		var_type = "gain"
	
	return {"Chr":row["Chr"],"Start":int(row["Start"]),"End":int(row["End"]),"var_type":var_type,"MVP_score":float(row["MVP_score"]),"SIFT_pred":float(row["SIFT_pred"]),"Polyphen2_HDIV_pred":float(row["Polyphen2_HDIV_pred"]),
	"Polyphen2_HVAR_pred":float(row["Polyphen2_HVAR_pred"]),"LRT_pred":float(row["LRT_pred"]),"MutationTaster_pred":float(row["MutationTaster_pred"]),
	"MutationAssessor_pred":float(row["MutationAssessor_pred"]),"FATHMM_pred":float(row["FATHMM_pred"]),"RadialSVM_pred":float(row["RadialSVM_pred"]),
	"LR_pred":float(row["LR_pred"]),"VEST3_score":float(row["VEST3_score"]),"CADD_phred":float(row["CADD_phred"]),"GERP_RS":float(row["GERP++_RS"]),
	"phyloP46way_placental":float(row["phyloP46way_placental"]),"phyloP100way_vertebrate":float(row["phyloP100way_vertebrate"]),
	"SiPhy_29way_logOdds":float(row["SiPhy_29way_logOdds"]),"CDTS_1st":float(row["CDTS_1st"]),"CDTS_5th":float(row["CDTS_5th"]),
	"gain_freq_AFR":float(row["gain_freq_AFR"]),"gain_freq_AMR":float(row["gain_freq_AMR"]),"gain_freq_ASJ":float(row["gain_freq_ASJ"]),
	"gain_freq_EAS":float(row["gain_freq_EAS"]),"gain_freq_FIN":float(row["gain_freq_FIN"]),"gain_freq_NFE":float(row["gain_freq_NFE"]),"gain_freq_OTH":float(row["gain_freq_OTH"]),
	"gain_freq_SAS":float(row["gain_freq_SAS"]),"gain_freq_UKN":float(row["gain_freq_UKN"]),"loss_freq_AFR":float(row["loss_freq_AFR"]),
	"loss_freq_AMR":float(row["loss_freq_AMR"]),"loss_freq_ASJ":float(row["loss_freq_ASJ"]),"loss_freq_EAS":float(row["loss_freq_EAS"]),
	"loss_freq_FIN":float(row["loss_freq_FIN"]),"loss_freq_NFE":float(row["loss_freq_NFE"]),"loss_freq_OTH":float(row["loss_freq_OTH"]),
	"loss_freq_SAS":float(row["loss_freq_SAS"]),"loss_freq_UKN":float(row["loss_freq_UKN"]),"gainFreq":float(row["gain.freq"]),"lossFreq":float(row["loss.freq"]),
	"pELS":float(row["pELS"]),"CTCF_bound":float(row["CTCF-bound"]),"PLS":float(row["PLS"]),"dELS":float(row["dELS"]),"CTCF_only":float(row["CTCF-only"]),
	"DNase_H3K4me3":float(row["DNase-H3K4me3"]),"pLI":float(row["pLI"]),"Episcore":float(row["Episcore"]),"GHIS":float(row["GHIS"])}
			
#XCNV
def do_xcnv(queries):
	
	#Write file
	f = open("/tmp/queries.bed",'w')
	f.write(queries)
	f.close()
			
	#Execute XCNV and convert result to regular dict
	os.system("cd ./XCNV/bin && ./XCNV /tmp/queries.bed")
	with open("/tmp/queries.output.csv") as csvfile:
		csvreader = csv.DictReader(csvfile)
		for row in csvreader:
						
			#Read the row
			xcnv_data = row2xcnv(json.loads(json.dumps(row)))
			print(xcnv_data)
					
			#Save to S3
			conn, bucket = getS3()
			setFile(bucket,"xcnv/" + xcnv_data["Chr"] + ":" + str(xcnv_data["Start"]) + "-" + str(xcnv_data["End"]) + ":" + xcnv_data["var_type"] + ".json",str(xcnv_data).replace("\'","\"") )
			conn.close()


#AWS Lambda Handler
def handler(event, context):
	queries = event["headers"]["queries"]
	do_xcnv(queries)
	return 200
