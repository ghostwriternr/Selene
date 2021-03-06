import pymongo
import sys, getopt
import time
import Queue
from pymongo import MongoClient
from collections import defaultdict

client = MongoClient()
db = client.fb_db
friendsCollection = db.network_dict
musicCollection = db.music_dict

def createNetworkGraphFromDB():
	edgeList = friendsCollection.find()
	networkG = defaultdict(list)
	for rowObject in edgeList:
		u = int(rowObject['u'])
		v = int(rowObject['v'])
		if v not in networkG[u]:
			networkG[u].append(v)
		if u not in networkG[v]:
			networkG[v].append(u)
	
	# print 'Printing Network Graph'
	# print len(networkG)
	# for u in networkG:
	# 	print u,
	# 	print ':',
	# 	for v in networkG[u]:
	# 		print v,
	# 	print '\n'

	return networkG


def createSongGraphFromDB():
	edgeList = musicCollection.find()
	musicG = defaultdict(list)
	for rowObject in edgeList:
		u = int(rowObject['userid'])
		song = str(rowObject['song'])
		musicG[u].append(song)
	return musicG

def neighboursTillDepthK(networkG,source,depth):
	# print 'Running BFS'
	Q = Queue.Queue()
	visited = {}
	level = {}
	neighbours = []
	Q.put(source)
	level[source] = 0
	while True:
		if Q.empty():
			break
		u = Q.get()
		if level[u] > 5:
			break
		visited[u] = True
		

		for v in networkG[u]:
			if v not in visited:
				Q.put(v)
				level[v] = level[u] + 1
				visited[v] = True
				neighbours.append(v)

	# print 'Printing neighbours of ' + str(source)
	# for v in neighbours:
	# 	print v,
	# print '\n'

	return neighbours

def populateMusicPreferences(clusterList,musicG):
	musicFrequencyDict = {}
	for user in clusterList:
		for song in musicG[user]:
			if(song not in musicFrequencyDict):
				musicFrequencyDict[song] = 1
			else:
				musicFrequencyDict[song] += 1
	return musicFrequencyDict


def getMostPopularSonginCluster(source):
	networkG = createNetworkGraphFromDB()

	musicG = createSongGraphFromDB()
	neighboursTillDepthFive = neighboursTillDepthK(networkG,source,5)
	clusterList = neighboursTillDepthFive
	clusterList.append(source)
	musicPreferences = populateMusicPreferences(clusterList,musicG)
	
	songs = list(musicPreferences.keys())
	frequency = list(musicPreferences.values())
	mostPopularSong = songs[frequency.index(max(frequency))]

	# print 'Printing Music Preferences in Cluster'
	# for song in songs:
	# 	print song,
	# print 'mostPopularSong: ' + str(mostPopularSong)

	return mostPopularSong


if __name__ == '__main__':
	getMostPopularSonginCluster(int(sys.argv[1]))
