import os
import json
import requests
import lxml.etree
#set the text mining uri

uri = ""
#Set the directory

DirectoryName = ""
Directory = os.fsencode(DirectoryName)
def extract_values(obj, key):
    #Pull all values of specified key from nested JSON
    arr = []

    def extract(obj, arr, key):
        #Recursively search for values of key in JSON tree.
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results
#Loop throug each file
for file in os.listdir(Directory) :
    #Get the filename
    filename = os.fsdecode(file)
    #Load the JSON file
     #Set the lists
    DISEASES = []
    SYMPTOMS = []
    DRUGS = []
    Locations = []
    ComplexConcepts =[]
    SimpleConcepts = []
    Categories = []
    with open(DirectoryName + filename) as json_file:
        #Load the json file
        data = json.load(json_file)
        #Look for all of the text value
        text = extract_values(data,'text')
        tcount =0
        for t in text:
            postheaders = {}
            postheaders['Content-Type'] = "application/xml"
            #Create the xml post add the text
            xml = "<?xml version=" + '"' + "1.0" + '"'+ " encoding=" + '"' + "UTF-8" + '"'+ " ?><Nserver><ResultEncoding>UTF-8</ResultEncoding><TextID>COVID</TextID><NSTEIN_Text>"+ t + "</NSTEIN_Text><LanguageID>ENGLISH</LanguageID><Methods><nconceptextractor><ExcludeEntities/><SimpleConcepts></SimpleConcepts><ComplexConcepts><RelevancyLevel>FIRST</RelevancyLevel></ComplexConcepts></nconceptextractor><nfinder><nfExtract><Cartridges><Cartridge>GL</Cartridge><Cartridge>DISEASES</Cartridge><Cartridge>DRUGS</Cartridge><Cartridge>SYMPTOMS</Cartridge></Cartridges></nfExtract><nfFullTextSearch><Cartridges><Cartridge>DISEASES</Cartridge><Cartridge>DRUGS</Cartridge><Cartridge>SYMPTOMS</Cartridge><Cartridge>GL</Cartridge></Cartridges></nfFullTextSearch></nfinder><nsentiment Name=" + '"' +"RequestName" + '"' + "><Name>Nstein</Name></nsentiment><ncategorizer><KBid>IPTC</KBid><NumberOfCategories>10</NumberOfCategories><RejectedCategories><NumberOfRejectedCategories>10</NumberOfRejectedCategories></RejectedCategories></ncategorizer></Methods></Nserver>"
            r = requests.post(uri,data=xml.encode('UTF-8'),headers=postheaders)
            if r.status_code != 200:
                continue
            #Get the results
            #sentiment
            root = lxml.etree.fromstring(r.content)
            sentiment = root.find('Results/nsentiment/DocumentLevel/Tone')
            if hasattr(sentiment,'text'):
                sentiment = sentiment.text
            #Get the Concepts
            #Complex
            complex_concepts = root.findall('Results/nconceptextractor/ComplexConcepts/Concept')
            for cc in complex_concepts:
                if hasattr(cc,'text'):
                    ComplexConcepts.append(cc.text)
            #Simple
            simple_concepts = root.findall('Results/nconceptextractor/SimpleConcepts/Concept')
            for sc in simple_concepts:
                if hasattr(sc,'text'):
                    SimpleConcepts.append(sc.text)
            #Get the Categories
            categories = root.findall('Results/ncategorizer/Categories/Category')
            for c in categories:
                if hasattr(c,'text'):
                    Categories.append(c.text)
            #Get the Entities
            FTResults = root.findall('Results/nfinder/nfFullTextSearch/ExtractedTerm')
            #Loop through all results
            for ft in FTResults:
                if 'CartridgeID' in ft.attrib:
                    ftType = ft.attrib['CartridgeID']
                    #Get the main term
                    for MTchild in ft:
                        if MTchild.tag == 'MainTerm':
                            MainTerm = MTchild.text
                            MT = ft.find('MainTerm')
                            if ftType == "DISEASES":
                                if MainTerm not in DISEASES:
                                    DISEASES.append(MainTerm)
                                if ftType == "SYMPTOMS":
                                    if MainTerm not in SYMPTOMS:
                                        SYMPTOMS.append(MainTerm)
                                if ftType == "DRUGS":
                                    if MainTerm not in DRUGS:
                                        DRUGS.append(MainTerm)
                                if ftType == "GL":
                                    if MainTerm not in Locations:
                                        Locations.append(MainTerm)
                        #Now get the Sub Terms
                            for STchild in MTchild:
                                if ftType == "DISEASES":
                                    if STchild.text not in DISEASES:
                                        DISEASES.append(STchild.text)
                                if ftType == "SYMPTOMS":
                                    if MainTerm not in SYMPTOMS:
                                        SYMPTOMS.append(MainTerm)
                                if ftType == "DRUGS":
                                    if MainTerm not in DRUGS:
                                        DRUGS.append(MainTerm)
                                if ftType == "GL":
                                    if MainTerm not in Locations:
                                        Locations.append(MainTerm)
            NFResults = root.findall('Results/nfinder/nfExtract/ExtractedTerm')
            #Loop through all results
            for nf in FTResults:
                if 'CartridgeID' in nf.attrib:
                    nfType = nf.attrib['CartridgeID']
                    #Get the main term
                    for MTchild in nf:
                        if MTchild.tag == 'MainTerm':
                            MainTerm = MTchild.text
                            MT = nf.find('MainTerm')
                            if nfType == "DISEASES":
                                if MainTerm not in DISEASES:
                                    DISEASES.append(MainTerm)
                            if nfType == "SYMPTOMS":
                                if MainTerm not in SYMPTOMS:
                                    SYMPTOMS.append(MainTerm)
                            if nfType == "DRUGS":
                                if MainTerm not in DRUGS:
                                    DRUGS.append(MainTerm)
                            if nfType == "GL":
                                if MainTerm not in Locations:
                                    Locations.append(MainTerm)
                        #Now get the Sub Terms
                        for STchild in MTchild:
                            if nfType == "DISEASES":
                                if STchild.text not in DISEASES:
                                    DISEASES.append(STchild.text)
                            if nfType == "SYMPTOMS":
                                if STchild.text not in SYMPTOMS:
                                    SYMPTOMS.append(STchild.text)
                            if nfType == "DRUGS":
                                if STchild.text not in DRUGS:
                                    DRUGS.append(STchild.text)
                            if nfType == "GL":
                                if STchild.text not in Locations:
                                    Locations.append(STchild.text)
            #Write the files out
            #text id
            textid=open("TextID.txt","a+")
            textid.write(str(tcount)+"_" + filename + "\n")
            textid.close
            print("Count " + str(tcount))
            #sentiment
            sent=open("Sentiment.txt","a+")
            sent.write(str(tcount)+"_" + filename + ";" + sentiment + "\n")
            sent.close
            #Write the diseases to file
            txtdis=open("DISEASES.txt","a+")
            for D in DISEASES:
                txtdis.write(str(tcount)+"_" + filename + ";" + D + ";" + "\n")
            txtdis.close
            #Write the Drugs to file
            txtdrugs=open("DRUGS.txt","a+")
            for dr in DRUGS:
                txtdrugs.write(str(tcount)+"_" + filename + ";" + dr + ";" + "\n")
            txtdrugs.close
            txtsymp=open("Symptoms.txt","a+")
            for s in SYMPTOMS:
                txtsymp.write(str(tcount)+"_" + filename + ";" + s + ";" + "\n")
            txtsymp.close
            ##Concepts
            txtcc=open("ComplexConcepts.txt","a+")
            for cc in ComplexConcepts:
                txtcc.write(str(tcount)+"_" + filename + ";" + cc + ";" + "\n")
            txtcc.close
            txtsc=open("SimpleConcepts.txt","a+")
            for sc in SimpleConcepts:
                txtsc.write(str(tcount)+"_" + filename + ";" + sc + ";" + "\n")
            txtsc.close
            #Locations
            txtL=open("Locations.txt","a+")
            for l in Locations:
                txtL.write(str(tcount)+"_" + filename + ";" + l + ";" + "\n")
            txtL.close
            #Categories
            txtcats=open("Categories.txt","a+")
            for cats in Categories:
                txtcats.write(str(tcount)+"_" + filename + ";" + cats + ";" + "\n")
            txtcats.close
            #Write the text and ID

            tcount = tcount + 1
    continue


