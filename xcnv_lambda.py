import os
import csv
import json
import sys

#MongoDB
from cloud.mongo import get_mongo_db

#Genomic coordinates
from coordinates import GenomicCoordinates

#Liftover
from liftover import ChainFile
os.system("cp -r chainfiles /tmp/chainfiles")
hg38to19_lifter = ChainFile("/tmp/chainfiles/hg38ToHg19.over.chain.gz","hg38","hg19")

#Open
client_db, db = get_mongo_db()
print("MongoDB connection opened")

#hg38 to hg19
def hg38to19(chromosome : str,pos : int):
    l = hg38to19_lifter[chromosome][pos]
    if len(l) == 0:
        return pos
    else:
        return l[0][1]
        
#Save to Mongo, made for updating CNV-Hub XCNV value
def save(title,row):
		
	#Find
	filt = {"title": title}
	cnv = db["cnvhub_results"].find_one(filt)
	
	#New XCNV value
	new_xcnv = { "$set": { 'xcnv': row } }
	
	#Update
	cnv = db["cnvhub_results"].update_one(filt,new_xcnv)
	
	#Saved message
	print(title,"xcnv value updated !")
	        
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

#Compute XCNV
def compute_xcnv(genomics_coordinates):

	f = open("/tmp/queries.bed",'w')
	for q in genomics_coordinates:
		s = q.start
		e = q.end
		if q.ref == "hg38":
			s = hg38to19(q.chr,q.start)
			e = hg38to19(q.chr,q.end)
		f.write(q.chr.replace("chr","") + "\t" + str(s) + "\t" + str(e) + "\t" + q.type + "\n")
	f.close()

	#Execute XCNV and convert result to regular dict
	os.system("cd /tmp/XCNV/bin && ./XCNV /tmp/queries.bed")
	with open("/tmp/queries.output.csv") as csvfile:
		csvreader = csv.DictReader(csvfile)
		
		#Save results
		nRow = 0
		for row in csvreader:
			xcnv_row = row2xcnv(row)
			query = genomics_coordinates[nRow]
			title = query.ref + "-" + query.chr + "-" + str(query.start) + "-" + str(query.end) + "-" + query.type
			save(title,xcnv_row)
			nRow += 1
		
#Build XCNV
def build_xcnv():
	print("Copying archive...")
	os.system("cp XCNV.tar.gz /tmp/XCNV.tar.gz")
	print("Untar archive...")
	os.system("cd /tmp && tar -xf XCNV.tar.gz")
	print("Chmod 755...")
	os.system("chmod -R 755 /tmp")
	print("Installing XCNV...")
	os.system("cd /tmp/XCNV && ./Install.sh")
	print("XCNV installed :) !")

#AWS Lambda Handler
def handler(event, context):
	
	#Build XCNV
	print("Start of XCNV lambda")
	build_xcnv()
	
	#Extract queries
	str_queries = event["headers"]["queries"]
	queries = str_queries.split("$$")
	
	#String to Genomic coordinates
	gc = []
	for query in queries:
		q = query.split("\t")
		gc.append(GenomicCoordinates(q[0],q[1],int(q[2]),int(q[3]),q[4]) )
	
	#Compute
	if len(gc) > 0:
		compute_xcnv(gc)
	else:
		print("No XCNV query")
		
	#Close
	client_db.close()
	print("Mongo DB connection closed")

	print("XCNV-Lambda finished !")
	return 200

#Test
#handler({"headers":{"queries":"hg19\tchr22\t18894835\t21798755\tloss"}},None)
#handler({"headers":{"queries":"hg19\tchr2\t1000000\t2000000\tgain$$hg19\tchr2\t1000000\t2000000\tloss"}},None)
