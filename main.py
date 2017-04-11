import pytumblr
import simplejson
import json
import time
import os
import threading
import urllib2
import exiftool
import subprocess
from concurrent.futures import ThreadPoolExecutor

client = pytumblr.TumblrRestClient(
  '****',
  '****',
  '****',
  '****'
)

blog_list = ["ifpaintingscouldtext"]

blog_cnt = len(blog_list)

sys_ts = [0]*blog_cnt

def worker(num):

	blog_name = blog_list[num]
	type_photo = 'photo'
	type_video = 'video'
	type_audio = 'audio'
	type_text = 'text'
	# Make the request
	tumblr_info_dict = client.blog_info(blog_name)
	#sys_ts[num] = tumblr_info_dict['blog']['updated']
	tumblr_posts = client.posts(blog_name, limit = 1)
	for i in range(len(tumblr_posts['posts'])):
		cur_ts = tumblr_posts['posts'][i]['timestamp']
		print cur_ts
		if cur_ts <= sys_ts[num]:
			break
		sys_ts[num] = cur_ts
		#print tumblr_posts['posts'][i]['summary']
		if tumblr_posts['posts'][i]['type'] == type_photo:
			photosdict = tumblr_posts['posts'][i]['photos']
			photo_cnt = len(photosdict)
			for j in range(photo_cnt):
				URL = photosdict[j]['original_size']['url']
				img = urllib2.urlopen(URL)
				localFile = open("/tmp/temp{0}.jpg".format(num), 'wb')
				localFile.write(img.read())
				localFile.close()
				msg = u"-i '/tmp/temp{0}.jpg'".format(num)
				with exiftool.ExifTool() as et:
					metadata = et.get_metadata("/tmp/temp{0}.jpg".format(num))				
				additional_info = ""
				if "EXIF:Make" in metadata.keys():
                                            additional_info += metadata["EXIF:Make"]+" "
				if "EXIF:Model" in metadata.keys():
					additional_info += metadata["EXIF:Model"]+"| "
				if "EXIF:FocalLength" in metadata.keys():
                                            additional_info += str(metadata["EXIF:FocalLength"])+"mm "
				if "EXIF:FNumber" in metadata.keys():
                                            additional_info += "F"+str(metadata["EXIF:FNumber"])+" "
				if "EXIF:ShutterSpeedValue" in metadata.keys():
                                            additional_info += "1/{0}".format(int(round(1/metadata["EXIF:ShutterSpeedValue"])))+" "
				if "EXIF:ISO" in metadata.keys():
                                            additional_info += "ISO"+str(metadata["EXIF:ISO"])+" "
				#msg +=" --caption '{0}{1}[ {2} ]'".format(blog_list[num], 'summary', additional_info)
				caption = u" --caption '{0}\n{1}\n[ {2} ]'".format(blog_list[num], tumblr_posts['posts'][i]['summary'], additional_info) 
			  	#print "msgs:"+msg
				subprocess.call(u'telegram-send '+msg+caption, shell=True)	
				#os.system("telegram-send -i"+" /tmp/temp{0}.jpg".format(num)+" --caption '{0}\n[ {1} ]'".format(blog_list[num], additional_info))
				print photosdict[j]['original_size']['url'];
		elif tumblr_posts['posts'][i]['type'] == type_video:
			msg = blog_list[num]+"(video)"+" "
			if tumblr_posts['posts'][i]['video_type'] == "vimeo":
				msg += tumblr_posts['posts'][i]['permalink_url']+" "+tumblr_posts['posts'][i]['summary']
			elif tumblr_posts['posts'][i]['video_type'] == "tumblr":
				msg += tumblr_posts['posts'][i]['video_url']+" "+tumblr_posts['posts'][i]['summary']
			#os.system("telegram-send " + msg)
			subprocess.call(['telegram-send', msg])	
		elif tumblr_posts['posts'][i]['type'] == type_audio:
			audio_url = ""
			if tumblr_posts['posts'][i]['audio_type'] == 'tumblr':
				tmp_url = tumblr_posts['posts'][i]['audio_url']
				audio_url = "http://a.tumblr.com/{0}o1.mp3".format(tmp_url[tmp_url.rfind('/')+1:])
			msg = blog_list[num]+"(audio)"+audio_url+" "+tumblr_posts['posts'][i]['summary']
			subprocess.call(['telegram-send', msg])
		elif tumblr_posts['posts'][i]['type'] == type_text:
			msg = blog_list[num]+"(text)"+" "+tumblr_posts['posts'][i]['summary']+"\n---body---\n"+tumblr_posts['posts'][i]['body']
			subprocess.call(['telegram-send', msg])


thread_cnt = len(blog_list)
pool = ThreadPoolExecutor(thread_cnt)

while True:
	for i in range(thread_cnt):
		future = pool.submit(worker, i)
	time.sleep(10)
