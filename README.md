# entity-matching
## Match entities between CiteSeerX and other digital libraries
In this project, we attempt to develop a machine learning (ML) based method to match paper entities between CiteSeerX and other digital libraries, including but not limited to the IEEE Xplore (IEEE hereafter), DBLP, Web of Science (WoS hereafter). Like most ML-based methods, data preprocessing takes substantial efforts. The purpose of creating this codebase is to centralize working programs that accomplish different tasks so they can be reused for future people that take over corresponding roles.

Models:

[HMM](HMM.py) (Header Matching Model): This model tries to match paper entities across data bases using information existing in the header of the papers including title, abstract, list of authors and venue. THis model is used for matching CiteSeerX to digital libraries without citation information such as DBLP, IEEE and Medline.

[CMM](CMM.py) (Citation Matching Model): This model leverages citations for matching of the papers if citation information exists. 

[TEM](TEM.py) (Title Evaluation Model): This model evaluates quality of the title. If title has a high quality, HMM model is used otherwise combination of CMM and HMM model is applied for the matching process. 

[IMM](IMM.py) (Integrated Matching Model): This model integrates HMM and CMM with the help of TEM. 


-----------------------------------------------------------------------------------------------------
Files:

[ground truth](groundtruth.txt): This files contains a list of matching papers between CiteSeerX and WoS. 

[Similarity Profile](similarityProfile.py): This file compares profiles of two papers from different data sources and measures their similarity score. This model has different features for variety of information in header. 



Contributors: Allen C. Ge, Athar Sefid, Jian Wu, Jing Zhao
