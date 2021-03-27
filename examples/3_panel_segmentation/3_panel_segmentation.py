from utils.panel_seg_utils import segment_panels
import cv2, numpy as np


im_path= r'./3-0_input_1.png'
tmp= segment_panels(im_path)

# images for each step --- merged into single horizontal strip
merged= [tmp['image']] + [x['im'] for x in tmp['debug']]
merged= np.concatenate(merged, axis=1)
cv2.imwrite(f"3-1_merged.png", merged)

# individual images
for i,x in enumerate(tmp['debug']):
	cv2.imwrite(f"3-{i+2}_{x['name']}.png", x['im'])