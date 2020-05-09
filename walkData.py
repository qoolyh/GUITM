import json
import xml.etree.ElementTree as xeTree

def walkData(rootNode, elementsList):
    elementsList.append(rootNode.attrib)
    for childNode in rootNode:
        walkData(childNode, elementsList)


path = "data/a4_b42/tar/a44/"
fileName = 'ru.mail.ui.SlideStackActivity15'
activities = {}
activities[fileName] = {}

xmlFileName = fileName
elementsList = []
xml_tree = xeTree.ElementTree(file = path + xmlFileName + ".xml")  # 文件路径
root = xml_tree.getroot()
for child in root:
    walkData(child, elementsList)

activities[xmlFileName]["elements"] = elementsList

with open(path + "activitiesSummaryForOne.json", 'w') as file_obj:
    json.dump(activities, file_obj)