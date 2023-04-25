import os 
import json 
import argparse
from tabulate import tabulate

def increment_dict(d, k, v, inc_type="list"):
	inc = [v] if inc_type=="list" else v
	if k in d:
		d[k] = d[k] + inc
	else:
		d[k] = inc
	return d

def compute_recall(obj1, obj2, detected, N):
	if obj1 in detected and obj2 in detected:
		count = 2
	elif obj1 in detected or obj2 in detected:
		count = 1
	else:
		count = 0

	return count/N, count

parser = argparse.ArgumentParser() 
parser.add_argument("--text_json", default="./text_spatial_rel_phrases.json", help="location of the dataset")
parser.add_argument("--od", default="owlvit")
parser.add_argument("--th", type=float, default=0.1)
parser.add_argument("--mo", default=None, help="specify which models to evaluate separated by comma. eg. glide,glide_cdm")
args = parser.parse_args() 

od_dict = {
	"detr-resnet-50": "facebook/detr-resnet-50", 
	"detr-resnet-101": "facebook/detr-resnet-101", 
	"yolos-base": "hustvl/yolos-base"
	}

if args.mo:
	mo_vals = args.mo.split(",")
else:
	mo_vals= ["glide", "glide_cdm", "dallemini", "cogview2", "dallev2", "stable-diffusion", "sd_cdm", "stable-diffusion-2-1"] 

print("Reading Data ...")
with open(args.text_json, 'r') as f:
	text_data = json.load(f)


def get_visor_n(visor_by_uniq_id):
	visor_1, visor_2, visor_3, visor_4 = 0, 0, 0, 0
	for uniq_id, scores in visor_by_uniq_id.items():
		if sum(scores) >= 4:
			visor_4 = visor_4 + 1
		if sum(scores) >= 3:
			visor_3 = visor_3 + 1
		if sum(scores) >= 2:
			visor_2 = visor_2 + 1
		if sum(scores) >= 1:
			visor_1 = visor_1 + 1

	NUM_UNIQ = len(visor_by_uniq_id)

	return [100*visor_1/NUM_UNIQ, 100*visor_2/NUM_UNIQ, 100*visor_3/NUM_UNIQ, 100*visor_4/NUM_UNIQ]


def get_visor_spatial(results, text_data, split_by_rel=False):
	objacc_both, objacc_A, objacc_B = 0, 0, 0
	visor_cond, visor_uncond = 0, 0
	both_count, count = 0, 0
	visor_by_uniq_id = {}

	for img_id, rr in results.items():
		uniq_id = int(img_id.split("_")[0])
		ann = text_data[uniq_id]
		text = ann["text"]
		obj1 = ann["obj_1_attributes"][0]
		obj2 = ann["obj_2_attributes"][0]
		rel = ann["rel_type"]
		N = ann["num_objects"]
		recall = rr["recall"]/N
		
		if rel=="and" or N!=2:
			continue
		detected = rr["classes"]
		det_objA = int(obj1 in detected)
		det_objB = int(obj2 in detected)
		det_both = int(obj1 in detected and obj2 in detected)
		sra = rr["sra"]
		objacc_both = objacc_both + det_both
		objacc_A = objacc_A + det_objA
		objacc_B = objacc_B + det_objB

		visor_cond = visor_cond + det_both*sra
		both_count = both_count + det_both
		count = count + 1
		visor_by_uniq_id = increment_dict(visor_by_uniq_id, uniq_id, det_both*sra)


	# visor scores
	visor_cond = 100*visor_cond/both_count 
	visor_n = get_visor_n(visor_by_uniq_id)

	# objacc scores
	objacc = [100*objacc_A/count, 100*objacc_B/count, 100*objacc_both/count]

	return visor_cond, visor_n, objacc


print("Processing ...")

visor_table_data = []

for j, mo in enumerate(mo_vals):
	visor_list = []
	fname = args.text_json.split('/')[-1][:-5]
	results_path = "od/results_{}_{}_{}_{}.json".format(
		mo, fname, args.od, args.th)

	if not os.path.exists(results_path):
		print("Results Path does not exist.")
		continue

	with open(results_path, "r") as f:
		results = json.load(f)
	num = len(results)
	visor_cond, visor_n, objacc = get_visor_spatial(
		results, text_data)
	visor_uncond = visor_cond * objacc[2]
	visor_table_data.append([
		mo, 
		f'{objacc[2]:.2f}', f'{visor_cond:.2f}', f'{0.01*(visor_uncond):.2f}',
		f'{visor_n[0]:.2f}', f'{visor_n[1]:.2f}', f'{visor_n[2]:.2f}', f'{visor_n[3]:.2f}', 
		str(num)
		])

print(
	tabulate(
		visor_table_data, 
		headers=[
			'Model', 
			'OA', 'VISOR_cond', 'VISOR_uncond',
			'VISOR_1', 'VISOR_2', 'VISOR_3', 'VISOR_4',  
			'Num_Imgs'
			]
		)
	)
