# Call syntax:
#   python3 OpenVokaWavMean-linux64.py path_to_sound_file.wav
#
# For the sound file hello.wav that comes with OpenVokaturi, the result should be:
#	Neutral: 0.760
#	Happy: 0.000
#	Sad: 0.238
#	Angry: 0.001
#	Fear: 0.000

import sys
import scipy.io.wavfile
from app.EmotionRecognition import Vokaturi
import os
from flask import jsonify

# Load model 1
Vokaturi.load("app/EmotionRecognition/emotion-lib-linux64.so")


def voiceSelection(file_name):
	# Reading sound file
	# file_name = sys.argv[1]
	(sample_rate, samples) = scipy.io.wavfile.read(file_name)
	# print ("Sample rate: %.3f Hz" % sample_rate)

	# Allocating sample array
	buffer_length = len(samples)
	# print ("Samples: %d" % (buffer_length))
	# print ("Channels: %d" % (samples.ndim))
	c_buffer = Vokaturi.SampleArrayC(buffer_length)
	if samples.ndim == 1:  # mono
		c_buffer[:] = samples[:] / 32768.0
	else:  # stereo
		c_buffer[:] = 0.5*(samples[:,0]+0.0+samples[:,1]) / 32768.0

	# Creating data structure
	voice = Vokaturi.Voice (sample_rate, buffer_length)
	# Filling data structure with samples
	voice.fill(buffer_length, c_buffer)

	# print ("Extracting emotions...")
	return voice


def model1GetNeutral(voice_Selection):
	quality = Vokaturi.Quality()
	emotionProbabilities = Vokaturi.EmotionProbabilities()
	voiceSelection(voice_Selection).extract(quality, emotionProbabilities)

	if quality.valid:
		print ("Neutral: %.3f" % emotionProbabilities.neutrality)
	else:
		print ("Not enough sonorancy to determine emotions")
	return


def model1GetHappy(voice_Selection):
	quality = Vokaturi.Quality()
	emotionProbabilities = Vokaturi.EmotionProbabilities()
	voiceSelection(voice_Selection).extract(quality, emotionProbabilities)

	if quality.valid:
		print ("Happy: %.3f" % emotionProbabilities.happiness)
	else:
		print ("Not enough sonorancy to determine emotions")
	return


def model1GetSad(voice_Selection):
	quality = Vokaturi.Quality()
	emotionProbabilities = Vokaturi.EmotionProbabilities()
	voiceSelection(voice_Selection).extract(quality, emotionProbabilities)

	if quality.valid:
		print ("Sad: %.3f" % emotionProbabilities.sadness)
	else:
		print ("Not enough sonorancy to determine emotions")
	return


def model1GetAngry(voice_Selection):
	quality = Vokaturi.Quality()
	emotionProbabilities = Vokaturi.EmotionProbabilities()
	voiceSelection(voice_Selection).extract(quality, emotionProbabilities)

	if quality.valid:
		print ("Angry: %.3f" % emotionProbabilities.anger)
	else:
		print ("Not enough sonorancy to determine emotions")
	return


def model1GetFear(voice_Selection):
	quality = Vokaturi.Quality()
	emotionProbabilities = Vokaturi.EmotionProbabilities()
	voiceSelection(voice_Selection).extract(quality, emotionProbabilities)

	if quality.valid:
		print ("Fear: %.3f" % emotionProbabilities.fear)
	else:
		print ("Not enough sonorancy to determine emotions")
	return


def model1GetResult(voice_Selection):
	quality = Vokaturi.Quality()
	emotionProbabilities = Vokaturi.EmotionProbabilities()
	voiceSelection(voice_Selection).extract(quality, emotionProbabilities)

	if quality.valid:
		result_of ={
		"request":"ok",
		"model": "1",
		"result":[ {
		"neutral":"%.3f"%emotionProbabilities.neutrality,
		"happy":"%3f"%emotionProbabilities.happiness,
		"sad":" %.3f" % emotionProbabilities.sadness,
		"angry":" %.3f" % emotionProbabilities.anger,
		"fear":" %.3f" % emotionProbabilities.fear
		}]}
	else:
		result_of={"request":"null", "result":[]}
	return result_of


def model1GetResultForAVA(voice_Selection):
	quality = Vokaturi.Quality()
	emotionProbabilities = Vokaturi.EmotionProbabilities()
	voiceSelection(voice_Selection).extract(quality, emotionProbabilities)
	if quality.valid:
		result_of ={
		"request":"ok",
		"model": "1",
		"result":[ {
		"neutral":"%.3f"%emotionProbabilities.neutrality,
		"happy":"%3f"%emotionProbabilities.happiness,
		"sad":" %.3f" % emotionProbabilities.sadness,
		"angry":" %.3f" % emotionProbabilities.anger,
		"fear":" %.3f" % emotionProbabilities.fear,
		"emotion": softmax([emotionProbabilities.anger,
							emotionProbabilities.happiness,
							emotionProbabilities.neutrality,
							emotionProbabilities.sadness,
							emotionProbabilities.fear])
		}]}
	else:
		result_of={"request":"null", "result":[]}
	return result_of
	

def softmax(emotions):
	index = emotions.index(max(emotions))
	if(index == 0):
		return 'A'
	elif(index == 1):
		return 'H'
	elif(index == 2):
		return 'N'
	elif(index == 3):
		return 'S'
	elif(index == 4):
		return 'F'


def parse_phone_number(phone):
    fixed_regions = {
        '26': '??????????',
        '25': '????',
        '86': '??????????',
        '24': '??????????',
        '23': '??????????',
        '81': '??????????',
        '28': '??????????',
        '31': '????????????',
        '44': '?????????????????? ????????',
        '11': '????????????????',
        '74': '???????????????? ?? ????????????????',
        '83': '????????????????',
        '51': '???????????? ????????',
        '45': '????????????',
        '17': '????????????',
        '41': '?????????????????? ????????',
        '54': '???????????? ?? ????????????????',
        '87': '??????????????',
        '71': '????????',
        '66': '????????????',
        '34': '??????????',
        '56': '???????????? ??????????',
        '13': '??????????',
        '77': '??????????',
        '76': '??????????????',
        '61': '??????????????',
        '38': '???????? ???????? ?? ??????????????',
        '58': '???????????? ??????????',
        '35': '??????',
        '84': '??????????',
        '21': '??????????'
    }

    mobile_operators = {
        '930': 'Irancell',
        '933': 'Irancell',
        '935': 'Irancell',
        '936': 'Irancell',
        '937': 'Irancell',
        '938': 'Irancell',
        '939': 'Irancell',
        '901': 'Irancell',
        '902': 'Irancell',
        '903': 'Irancell',
        '904': 'Irancell',
        '905': 'Irancell',
        '941': 'Irancell',
        '910': 'MCI',
        '911': 'MCI',
        '912': 'MCI',
        '913': 'MCI',
        '914': 'MCI',
        '915': 'MCI',
        '916': 'MCI',
        '917': 'MCI',
        '918': 'MCI',
        '919': 'MCI',
        '990': 'MCI',
        '991': 'MCI',
        '992': 'MCI',
        '932': 'Talia',
        '920': 'RighTel',
        '921': 'RighTel',
        '922': 'RighTel',
        '931': 'MTCE',
        '934': 'TeleKish',
        '999': 'MVNO',
        '998': 'Shatel',
        '994': 'Anarestan',
    }

    mobile_regions = {
        '930': '??????????',
        '933': '??????????',
        '935': '??????????',
        '936': '??????????',
        '937': '??????????',
        '938': '??????????',
        '939': '??????????',
        '901': '??????????',
        '902': '??????????',
        '903': '??????????',
        '904': '??????????',
        '905': '??????????',
        '941': '??????????',
        '910': '??????????',
        '911': '????????????????',
        '912': '??????????',
        '913': '????????????',
        '914': '?????????????????? ????????',
        '915': '???????????? ????????',
        '916': '??????????????',
        '917': '????????',
        '918': '??????????',
        '919': '??????????',
        '990': '??????????',
        '991': '??????????',
        '992': '??????????',
        '932': '??????????',
        '920': '??????????',
        '921': '??????????',
        '922': '??????????',
        '931': '??????????',
        '934': '??????',
        '999': '??????????',
        '998': '??????????',
        '994': '??????????',
    }

    if phone == 'anonymous':
        return {
            'type': 'Unknown',
            'region': 'Unknown',
            'operator': 'Unknown'
        }

    if len(phone) < 8:
        return {
            'type': 'Unknown',
            'region': 'Unknown',
            'operator': 'Unknown'
        }

    if len(phone) > 10:
        phone = phone[-10:]

    if phone[0] == '0':
        return {
            'type': 'Unknown',
            'region': 'Unknown',
            'operator': 'Unknown'
        }

    if len(phone) == 8:
        type = 'F'
        region = '??????????'
        operator = 'TCI'
    elif phone[0:1] == '9':
        type = 'M'
        operator = mobile_operators[phone[0:3]]
        region = mobile_regions[phone[0:3]]
    else:
        type = 'F'
        operator = 'TCI'
        try:
            region = fixed_regions[phone[0:2]]
        except:
            print(phone)
            region = 'Unknown'

    return {
        'type': type,
        'region': region,
        'operator': operator
    }