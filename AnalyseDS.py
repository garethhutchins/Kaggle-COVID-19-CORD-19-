import os
import json
import requests
import lxml.etree
#set the text mining uri

uri = ""
#Set the directory
DirectoryName = "C:/Users/ghutchin/Documents/Work/COVID-19 Kaggle/Data/biorxiv_medrxiv/biorxiv_medrxiv/"
#DirectoryName = "C:/Users/ghutchin/Documents/Work/COVID-19 Kaggle/Data/comm_use_subset/comm_use_subset/"
#DirectoryName = "C:/Users/ghutchin/Documents/Work/COVID-19 Kaggle/Data/custom_license/custom_license/"
#DirectoryName = "C:/Users/ghutchin/Documents/Work/COVID-19 Kaggle/Data/noncomm_use_subset/noncomm_use_subset/"

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
    Epidemics = []
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
            #xml = "<?xml version=" + '"' + "1.0" + '"'+ " encoding=" + '"' + "UTF-8" + '"'+ " ?><Nserver><ResultEncoding>UTF-8</ResultEncoding><TextID>COVID</TextID><NSTEIN_Text>"+ t + "</NSTEIN_Text><LanguageID>ENGLISH</LanguageID><Methods><nconceptextractor><ExcludeEntities/><SimpleConcepts></SimpleConcepts><ComplexConcepts><RelevancyLevel>FIRST</RelevancyLevel></ComplexConcepts></nconceptextractor><nfinder><nfExtract><Cartridges><Cartridge>GL</Cartridge><Cartridge>DISEASES</Cartridge><Cartridge>DRUGS</Cartridge><Cartridge>SYMPTOMS</Cartridge></Cartridges></nfExtract><nfFullTextSearch><Cartridges><Cartridge>DISEASES</Cartridge><Cartridge>DRUGS</Cartridge><Cartridge>SYMPTOMS</Cartridge><Cartridge>GL</Cartridge></Cartridges></nfFullTextSearch></nfinder><nsentiment Name=" + '"' +"RequestName" + '"' + "><Name>Nstein</Name></nsentiment><ncategorizer><KBid>IPTC</KBid><NumberOfCategories>10</NumberOfCategories><RejectedCategories><NumberOfRejectedCategories>10</NumberOfRejectedCategories></RejectedCategories></ncategorizer></Methods></Nserver>"
            xml = "<?xml version=" + '"' + "1.0" + '"'+ " encoding=" + '"' + "UTF-8" + '"'+ " ?><Nserver><ResultEncoding>UTF-8</ResultEncoding><TextID>COVID</TextID><NSTEIN_Text>"+ t + "</NSTEIN_Text><LanguageID>ENGLISH</LanguageID><Methods><nconceptextractor><ExcludeEntities/><SimpleConcepts></SimpleConcepts><ComplexConcepts><RelevancyLevel>FIRST</RelevancyLevel></ComplexConcepts></nconceptextractor><nfinder><nfExtract><Cartridges><Cartridge>GL</Cartridge><Cartridge>DISEASES</Cartridge><Cartridge>DRUGS</Cartridge><Cartridge>SYMPTOMS</Cartridge></Cartridges></nfExtract><nfFullTextSearch><Cartridges><Cartridge>Epidemics</Cartridge><Cartridge>DISEASES</Cartridge><Cartridge>DRUGS</Cartridge><Cartridge>SYMPTOMS</Cartridge><Cartridge>GL</Cartridge></Cartridges></nfFullTextSearch></nfinder><nsentiment Name=" + '"' +"RequestName" + '"' + "><Name>Nstein</Name></nsentiment><ncategorizer><KnowledgeBase><KBid>IPTC</KBid><NumberOfCategories>10</NumberOfCategories></KnowledgeBase><KnowledgeBase><KBid>MeSHLite</KBid><NumberOfCategories>10</NumberOfCategories></KnowledgeBase></ncategorizer></Methods></Nserver>"
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
            categories = root.findall('Results/ncategorizer/KnowledgeBase/Categories/Category')
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
                                if ftType == "Epidemics":
                                    if MainTerm not in Epidemics:
                                        Epidemics.append(MainTerm)
                        #Now get the Sub Terms
                            for STchild in MTchild:
                                if ftType == "DISEASES":
                                    if STchild.text not in DISEASES:
                                        DISEASES.append(STchild.text)
                                if STchild.text == "SYMPTOMS":
                                    if MainTerm not in SYMPTOMS:
                                        SYMPTOMS.append(STchild.text)
                                if STchild.text == "DRUGS":
                                    if MainTerm not in DRUGS:
                                        DRUGS.append(STchild.text)
                                if ftType == "GL":
                                    if STchild.text not in Locations:
                                        Locations.append(STchild.text)
                                if ftType == "Epidemics":
                                    if STchild.text not in Epidemics:
                                        Epidemics.append(STchild.text)
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
                            if nfType == "Epidemics":
                                if MainTerm not in Epidemics:
                                    Epidemics.append(STchild.text)
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
                            if nfType == "Epidemics":
                                if MainTerm not in Epidemics:
                                    Epidemics.append(STchild.text)
            #Write the files out
            #text id
            textid=open("TextID.txt","a+", encoding="utf-8")
            textid.write(str(tcount)+"_" + str(filename) + "\n")
            textid.close
            print("Count " + str(tcount))
            #sentiment
            sent=open("Sentiment.txt","a+", encoding="utf-8")
            sent.write(str(tcount)+"_" + filename + ";" + str(sentiment) + "\n")
            sent.close
            #Write the diseases to file
            txtdis=open("DISEASES.txt","a+", encoding="utf-8")
            for D in DISEASES:
                txtdis.write(str(tcount)+"_" + filename + ";" + str(D) + ";" + "\n")
            txtdis.close
            #Write the Drugs to file
            txtdrugs=open("DRUGS.txt","a+", encoding="utf-8")
            for dr in DRUGS:
                txtdrugs.write(str(tcount)+"_" + filename + ";" + str(r) + ";" + "\n")
            txtdrugs.close
            txtsymp=open("Symptoms.txt","a+", encoding="utf-8")
            for s in SYMPTOMS:
                txtsymp.write(str(tcount)+"_" + filename + ";" + str(s) + ";" + "\n")
            txtsymp.close
            ##Concepts
            txtcc=open("ComplexConcepts.txt","a+", encoding="utf-8")
            for cc in ComplexConcepts:
                txtcc.write(str(tcount)+"_" + filename + ";" + str(cc) + ";" + "\n")
            txtcc.close
            txtsc=open("SimpleConcepts.txt","a+", encoding="utf-8")
            for sc in SimpleConcepts:
                txtsc.write(str(tcount)+"_" + filename + ";" + str(sc) + ";" + "\n")
            txtsc.close
            #Locations
            txtL=open("Locations.txt","a+", encoding="utf-8")
            for l in Locations:
                txtL.write(str(tcount)+"_" + filename + ";" + str(l) + ";" + "\n")
            txtL.close
            #Categories
            txtcats=open("Categories.txt","a+", encoding="utf-8")
            for cats in Categories:
                txtcats.write(str(tcount)+"_" + filename + ";" + str(cats) + ";" + "\n")
            txtcats.close
             #Epidemics
            txteps=open("Epidemics.txt","a+", encoding="utf-8")
            for eps in Epidemics:
                txteps.write(str(tcount)+"_" + filename + ";" + str(eps) + ";" + "\n")
            txteps.close
            #Write the text and ID

            tcount = tcount + 1
    continue


