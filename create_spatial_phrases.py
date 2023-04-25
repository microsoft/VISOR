import json 
import random
import argparse 
import itertools 
import re
import inflect

inflect_engine = inflect.engine()

random.seed(381)
parser = argparse.ArgumentParser() 
parser.add_argument("--rel_type", default="exact")
parser.add_argument("--shapes", type=str, default="all")
args = parser.parse_args() 

if args.shapes == "tiny":
	SHAPES = ["chair", "microwave", "cup", "book", "suitcase", "banana"]
else:
	SHAPES = [
	    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
	    'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
	    'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse',
	    'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
	    'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis',
	    'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
	    'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass',
	    'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich',
	    'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
	    'chair', 'couch', 'potted plant', 'bed', 'dining table',
	    'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard',
	    'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator',
	    'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
	    'toothbrush'
		]
NC2_COMBOS = list(itertools.combinations(SHAPES, 2))
RELATIONS = ["to the left of", "to the right of", "above", "below"]
RELATIONS_SHORT = {"to the left of": "left", "to the right of": "right", "above": "above", "below": "below"}

data = []
count = 0
################ two objects: ################
for (s1, s2) in NC2_COMBOS:
	# r = random.choice(RELATIONS[args.rel_type])
	articled_s1 = inflect_engine.a(s1)
	articled_s2 = inflect_engine.a(s2)
	for r in RELATIONS:
		# 1-rel-2
		text_rel_12 = " ".join([articled_s1, r, articled_s2])
		data.append({
			"unique_id": count, 
			"num_objects": 2, 
			"obj_1_attributes": [s1], 
			"obj_2_attributes": [s2], 
			"rel_type": r, 
			"text": text_rel_12
			})
		count = count + 1

		# 2-rel-1
		text_rel_21 = " ".join([articled_s2, r, articled_s1])
		data.append({
			"unique_id": count, 
			"num_objects": 2, 
			"obj_1_attributes": [s2], 
			"obj_2_attributes": [s1], 
			"rel_type": r, 
			"text": text_rel_21
			})
		count = count + 1

	# 1-and-2
	text_and_12 = " ".join([articled_s1, "and", articled_s2])	
	data.append({
		"unique_id": count, 
		"num_objects": 2, 
		"obj_1_attributes": [s1], 
		"obj_2_attributes": [s2], 
		"rel_type": "and", 
		"text": text_and_12
		})
	count = count + 1

	# 2-and-1
	text_and_21 = " ".join([articled_s2, "and", articled_s1])	
	data.append({
		"unique_id": count, 
		"num_objects": 2, 
		"obj_1_attributes": [s2], 
		"obj_2_attributes": [s1], 
		"rel_type": "and", 
		"text": text_and_21
		})
	count = count + 1

for s in SHAPES:
	articled_s = inflect_engine.a(s)
	text_single = articled_s
	data.append({
		"unique_id": count, 
		"num_objects": 1, 
		"obj_1_attributes": [s], 
		"obj_2_attributes": [None], 
		"rel_type": "single", 
		"text": text_single
		})
	count = count + 1

with open('text_spatial_rel_phrases.json', 'w') as f:
	json.dump(data, f, indent=2)
