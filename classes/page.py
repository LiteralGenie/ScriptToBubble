from utils.panel_seg_utils import segment_panels, arc_length
from .bbox import Bbox
import cv2, numpy as np


class Panel:
	def __init__(self, contour, page):
		self.contour= contour
		self.page= page

		mask= np.zeros(self.page.image.shape, np.uint8)
		self.mask= cv2.drawContours(mask, [contour], -1, (255,)*3 , -1)
		self.region= np.bitwise_and(self.mask, self.page.image)

		bbox= list(cv2.boundingRect(contour))
		bbox[1]= bbox[1] + bbox[3] - 1 # move y-coord to bottom left of bbox
		self.bbox= Bbox(*bbox)

		self.moments= cv2.moments(cv2.cvtColor(self.region, cv2.COLOR_BGR2GRAY))
		self.cx = self.moments['m10'] / self.moments['m00']
		self.cy = self.moments['m01'] / self.moments['m00']

	def __str__(self): # for debugger
		return f"{(int(self.cx),int(self.cy))} | " + str(self.bbox)

class PanelGroup:
	def __init__(self, lst, parent):
		self.items= lst
		self.parent= parent

	def __add__(self, other):
		self.items+= other.items

	def __len__(self):
		return len(self.items)

	def add_child(self, it):
		self.items.append(it)

	def get_closest(self, ref_point=None):
		if ref_point is None:
			ref_point= (0,0)
		def gt(a,b):
			da= arc_length((a.cx,a.cy), ref_point)
			db= arc_length((b.cx,b.cy), ref_point)
			return da > db

		first= None
		for x in self.items:
			if isinstance(x, PanelGroup):
				tmp= x.get_closest()
				if first is None or gt(tmp, first):
					first= tmp
			else:
				if first is None or gt(x, first):
					first= x

		return first

class Page:
	def __init__(self, im_path):
		tmp= segment_panels(im_path)

		self.image= tmp['image']
		self.panels= self.get_panels(tmp['contours'])
		for i,x in enumerate(tmp['debug']):
			cv2.imwrite(f"{x['name']}.png", x['im'])

	# todo: test
	# convert contours to Panel instances and order them by reading-order
	def get_panels(self, contours):
		def chk_height(to_search, to_check, thresh=0.9):
			thresh= thresh + (1-thresh)/2
			ts= to_search.bbox
			tc= to_check

			min_y= (1/thresh)*(ts.y-ts.height)
			max_y= (thresh)*ts.y
			return min_y <= tc.cy <= max_y
		def chk_width(panel, thresh=0.85):
			return (panel.bbox.width / self.image.shape[1]) >= thresh

		groups= PanelGroup([], None)
		for x in contours:
			groups.add_child(Panel(x, self))
			
		flag= True
		last_panel= groups.get_closest()
		while flag:
			flag= False

			if chk_width(last_panel):



		return groups

	def _debug_panels(self):
		debug= self.image.copy()
		for i,x in enumerate(self.panels):
			cmax= min(50+i*25, 255)
			cv2.drawContours(debug, [x.contour], -1, (150,200,cmax), (i+1)+3)
			cv2.drawMarker(debug, (int(x.cx),int(x.cy)), (0,255,0), thickness=3)
			cv2.putText(debug, f"PANEL {i}", (int(x.cx),int(x.cy)),
						cv2.FONT_HERSHEY_SIMPLEX, 20, (0,0,255), 2)

		cv2.imshow('.', debug)

		for i,x in enumerate(self.panels):
			cv2.imshow('..', x.region)
			cv2.waitKey(0)

		cv2.destroyAllWindows()

def get_range_overlap(r1, r2):
	s1,e1= r1
	s2,e2= r2

	# check no overlap
	if s1 < e2 or s2 < e1:
		return 0

	# overlap range is max(starting points) to min(ending points)
	return max(s1,s2), min(e1,e2)