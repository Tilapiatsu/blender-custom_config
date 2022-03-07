import bpy
import os, csv, codecs #辞書

def preference():
	preference = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences

	return preference


# 翻訳辞書の取得
def GetTranslationDict():
	dict = {}
	path = os.path.join(os.path.dirname(__file__), "translation_dictionary.csv")

	with codecs.open(path, 'r', 'utf-8') as f:
		reader = csv.reader(f)
		dict['ja_JP'] = {}
		for row in reader:
			for context in bpy.app.translations.contexts:
				dict['ja_JP'][(context, row[1].replace('\\n', '\n'))] = row[0].replace('\\n', '\n')

	return dict
