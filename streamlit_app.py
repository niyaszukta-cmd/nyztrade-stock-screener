import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
from functools import wraps
from io import BytesIO

st.set_page_config(page_title="NYZTrade Stock Screener", page_icon="🔍", layout="wide")

def check_password():
    def password_entered():
        username = st.session_state["username"].strip().lower()
        password = st.session_state["password"]
        users = {"demo": "demo123", "premium": "premium123", "niyas": "nyztrade123"}
        if username in users and password == users[username]:
            st.session_state["password_correct"] = True
            st.session_state["authenticated_user"] = username
            del st.session_state["password"]
            return
        st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        st.markdown("<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem; border-radius: 20px; text-align: center;'><h1 style='color: white;'>NYZTrade Stock Screener</h1></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.button("Login", on_click=password_entered, use_container_width=True)
            st.info("demo/demo123 | premium/premium123")
        return False
    elif not st.session_state["password_correct"]:
        st.error("Incorrect credentials")
        return False
    return True

if not check_password():
    st.stop()

st.markdown("""
<style>
.main-header{background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);padding:2.5rem;border-radius:20px;text-align:center;color:white;margin-bottom:2rem;box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);}
.metric-card{background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);padding:1.5rem;border-radius:15px;color:white;text-align:center;margin:1rem 0;}
.positive{background-color: #e8f5e9; color: #2e7d32; padding: 0.3rem; border-radius: 5px; font-weight: bold;}
.negative{background-color: #ffebee; color: #c62828; padding: 0.3rem; border-radius: 5px; font-weight: bold;}
.neutral{background-color: #fff3e0; color: #ef6c00; padding: 0.3rem; border-radius: 5px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# Combined Stock Database
MIDCAP_STOCKS = {
    "ANGELONE.NS":"Angel One","ANANDRATHI.NS":"Anand Rathi","AAVAS.NS":"Aavas Financiers","BAJAJFINSV.NS":"Bajaj Finserv",
    "CDSL.NS":"CDSL","CHOLAFIN.NS":"Cholamandalam Investment","CREDITACC.NS":"CreditAccess Grameen","CRISIL.NS":"CRISIL",
    "CSB.NS":"CSB Bank","EQUITAS.NS":"Equitas Holdings","FEDERALBNK.NS":"Federal Bank","FINOPB.NS":"Fino Payments",
    "HDFCAMC.NS":"HDFC AMC","IIFL.NS":"IIFL Finance","IIFLSEC.NS":"IIFL Securities","IRFC.NS":"IRFC",
    "ISEC.NS":"ICICI Securities","JMFINANCIL.NS":"JM Financial","KALYANKJIL.NS":"Kalyan Jewellers","KFINTECH.NS":"KFin Technologies",
    "LICHSGFIN.NS":"LIC Housing","MASFIN.NS":"MAS Financial","MOTILALOFS.NS":"Motilal Oswal","MUTHOOTFIN.NS":"Muthoot Finance",
    "PNBHOUSING.NS":"PNB Housing","RBL.NS":"RBL Bank","SBFC.NS":"SBFC Finance","STARHEALTH.NS":"Star Health",
    "UJJIVAN.NS":"Ujjivan Small Finance","UTIAMC.NS":"UTI AMC","AUBANK.NS":"AU Small Finance","BANDHANBNK.NS":"Bandhan Bank",
    "IDFCFIRSTB.NS":"IDFC First Bank","INDUSINDBK.NS":"IndusInd Bank","BANKBARODA.NS":"Bank of Baroda","CANBK.NS":"Canara Bank",
    "UNIONBANK.NS":"Union Bank","CENTRALBK.NS":"Central Bank","INDIANB.NS":"Indian Bank","IOB.NS":"Indian Overseas Bank",
    "BANKINDIA.NS":"Bank of India","MAHABANK.NS":"Bank of Maharashtra","KARNATBNK.NS":"Karnataka Bank","DCBBANK.NS":"DCB Bank",
    "ICICIGI.NS":"ICICI Lombard","ICICIPRULI.NS":"ICICI Prudential Life","SBILIFE.NS":"SBI Life","HDFCLIFE.NS":"HDFC Life",
    "MAXHEALTH.NS":"Max Healthcare","POLICYBZR.NS":"PB Fintech","NUVOCO.NS":"Nuvoco Vistas","SPANDANA.NS":"Spandana Sphoorty",
    "SWANENERGY.NS":"Swan Energy","BAJAJHLDNG.NS":"Bajaj Holdings","MAHLIFE.NS":"Mahindra Lifespace","TATAINVEST.NS":"Tata Investment",
    "SUNDARMFIN.NS":"Sundaram Finance","SHRIRAMFIN.NS":"Shriram Finance","MANAPPURAM.NS":"Manappuram Finance","COFORGE.NS":"Coforge",
    "CYIENT.NS":"Cyient","ECLERX.NS":"eClerx Services","HAPPSTMNDS.NS":"Happiest Minds","INTELLECT.NS":"Intellect Design",
    "KPITTECH.NS":"KPIT Technologies","LTIM.NS":"LTIMindtree","MASTEK.NS":"Mastek","MPHASIS.NS":"Mphasis",
    "NEWGEN.NS":"Newgen Software","NIITLTD.NS":"NIIT Ltd","OFSS.NS":"Oracle Financial","PERSISTENT.NS":"Persistent Systems",
    "ZENSAR.NS":"Zensar Technologies","ROUTE.NS":"Route Mobile","DATAMATICS.NS":"Datamatics Global","SONATSOFTW.NS":"Sonata Software",
    "SASKEN.NS":"Sasken Technologies","TATAELXSI.NS":"Tata Elxsi","TECHM.NS":"Tech Mahindra","3MINDIA.NS":"3M India",
    "AFFLE.NS":"Affle India","EASEMYTRIP.NS":"EaseMyTrip","ZOMATO.NS":"Zomato","NYKAA.NS":"Nykaa",
    "PAYTM.NS":"Paytm","BLUESTARCO.NS":"Blue Star","CAMPUS.NS":"Campus Activewear","DIXON.NS":"Dixon Technologies",
    "HLEGLAS.NS":"HLE Glascoat","HONAUT.NS":"Honeywell Automation","LXCHEM.NS":"Laxmi Organic","RPTECH.NS":"RP Tech India",
    "AMBER.NS":"Amber Enterprises","SYMPHONY.NS":"Symphony","VOLTAS.NS":"Voltas","WHIRLPOOL.NS":"Whirlpool India",
    "VGUARD.NS":"V-Guard Industries","CROMPTON.NS":"Crompton Greaves","HAVELLS.NS":"Havells India","ORIENTELEC.NS":"Orient Electric",
    "INDIAMART.NS":"IndiaMART","JUSTDIAL.NS":"Just Dial","MATRIMONY.NS":"Matrimony.com","NAZARA.NS":"Nazara Technologies",
    "SHOPERSTOP.NS":"Shoppers Stop","TATACOMM.NS":"Tata Communications","TATATECH.NS":"Tata Technologies","TEAMLEASE.NS":"TeamLease Services",
    "CARTRADE.NS":"CarTrade Tech","LATENTVIEW.NS":"LatentView Analytics","MPSLTD.NS":"MPS Limited","RAINBOW.NS":"Rainbow Children",
    "REDINGTON.NS":"Redington","STLTECH.NS":"Sterlite Technologies","SUBROS.NS":"Subros","SUPRAJIT.NS":"Suprajit Engineering",
    "SWARAJENG.NS":"Swaraj Engines","TANLA.NS":"Tanla Platforms","TCNSBRANDS.NS":"TCNS Clothing","TIMKEN.NS":"Timken India",
    "TRIVENI.NS":"Triveni Turbine","TTKHLTCARE.NS":"TTK Healthcare","TTKPRESTIG.NS":"TTK Prestige","VIPIND.NS":"VIP Industries",
    "VSTIND.NS":"VST Industries","WELSPUNIND.NS":"Welspun India","WESTLIFE.NS":"Westlife Development","POLYCAB.NS":"Polycab India",
    "AARTIDRUGS.NS":"Aarti Drugs","ABBOTINDIA.NS":"Abbott India","AJANTPHARM.NS":"Ajanta Pharma","ALEMBICLTD.NS":"Alembic Pharma",
    "ALKEM.NS":"Alkem Laboratories","ASTRAZEN.NS":"AstraZeneca Pharma","AUROBINDO.NS":"Aurobindo Pharma","BIOCON.NS":"Biocon",
    "CADILAHC.NS":"Cadila Healthcare","CAPLIPOINT.NS":"Caplin Point","CIPLA.NS":"Cipla","DIVISLAB.NS":"Divi's Laboratories",
    "DRREDDY.NS":"Dr Reddy's Labs","ERIS.NS":"Eris Lifesciences","FINEORG.NS":"Fine Organic","GLENMARK.NS":"Glenmark Pharma",
    "GLAXO.NS":"GlaxoSmithKline","GRANULES.NS":"Granules India","IPCALAB.NS":"IPCA Laboratories","JBCHEPHARM.NS":"JB Chemicals",
    "LUPIN.NS":"Lupin","MANKIND.NS":"Mankind Pharma","METROPOLIS.NS":"Metropolis Healthcare","NATCOPHARM.NS":"Natco Pharma",
    "PFIZER.NS":"Pfizer","SANOFI.NS":"Sanofi India","SOLARA.NS":"Solara Active","SUNPHARMA.NS":"Sun Pharma",
    "SYNGENE.NS":"Syngene International","TORNTPHARM.NS":"Torrent Pharma","WOCKPHARMA.NS":"Wockhardt","ZYDUSLIFE.NS":"Zydus Lifesciences",
    "ZYDUSWELL.NS":"Zydus Wellness","APOLLOHOSP.NS":"Apollo Hospitals","FORTIS.NS":"Fortis Healthcare","LALPATHLAB.NS":"Dr Lal PathLabs",
    "THYROCARE.NS":"Thyrocare","KRSNAA.NS":"Krsnaa Diagnostics","KIMS.NS":"KIMS Hospitals","MEDANTA.NS":"Global Health Medanta",
    "POLYMED.NS":"Poly Medicure","STAR.NS":"Strides Pharma","SUVEN.NS":"Suven Pharma","SEQUENT.NS":"Sequent Scientific",
    "SHILPAMED.NS":"Shilpa Medicare","BLISSGVS.NS":"Bliss GVS Pharma","INDOCO.NS":"Indoco Remedies","JUBLPHARMA.NS":"Jubilant Pharma",
    "LAURUS.NS":"Laurus Labs","MARKSANS.NS":"Marksans Pharma","NEULANDLAB.NS":"Neuland Laboratories","ASHOKLEY.NS":"Ashok Leyland",
    "BAJAJ-AUTO.NS":"Bajaj Auto","BALKRISIND.NS":"Balkrishna Industries","BHARATFORG.NS":"Bharat Forge","BOSCHLTD.NS":"Bosch",
    "EICHERMOT.NS":"Eicher Motors","ESCORTS.NS":"Escorts Kubota","EXIDEIND.NS":"Exide Industries","FORCEMOT.NS":"Force Motors",
    "HEROMOTOCO.NS":"Hero MotoCorp","M&M.NS":"Mahindra & Mahindra","MARUTI.NS":"Maruti Suzuki","MRF.NS":"MRF",
    "TATAMOTORS.NS":"Tata Motors","TVSMOTOR.NS":"TVS Motor","AMARAJABAT.NS":"Amara Raja","APOLLOTYRE.NS":"Apollo Tyres",
    "CRAFTSMAN.NS":"Craftsman Automation","ENDURANCE.NS":"Endurance Technologies","FINCABLES.NS":"Finolex Cables","JKTYRE.NS":"JK Tyre",
    "MAHINDCIE.NS":"Mahindra CIE","MOTHERSON.NS":"Motherson Sumi","SANDHAR.NS":"Sandhar Technologies","SANSERA.NS":"Sansera Engineering",
    "SCHAEFFLER.NS":"Schaeffler India","SKFINDIA.NS":"SKF India","TUBE.NS":"Tube Investments","WHEELS.NS":"Wheels India",
    "ABB.NS":"ABB India","AIAENG.NS":"AIA Engineering","ALICON.NS":"Alicon Castalloy","APOLLOPIPE.NS":"Apollo Pipes",
    "ASAHIINDIA.NS":"Asahi India Glass","CEATLTD.NS":"CEAT","CUMMINSIND.NS":"Cummins India","ELGIRUBCO.NS":"Elgi Rubber",
    "GABRIEL.NS":"Gabriel India","GREAVESCOT.NS":"Greaves Cotton","JAMNAAUTO.NS":"Jamna Auto","ABFRL.NS":"Aditya Birla Fashion",
    "AKZOINDIA.NS":"Akzo Nobel","AVANTIFEED.NS":"Avanti Feeds","BAJAJELEC.NS":"Bajaj Electricals","BATAINDIA.NS":"Bata India",
    "BIKAJI.NS":"Bikaji Foods","BRITANNIA.NS":"Britannia Industries","CCL.NS":"CCL Products","COLPAL.NS":"Colgate Palmolive",
    "DABUR.NS":"Dabur India","EMAMILTD.NS":"Emami","GILLETTE.NS":"Gillette India","GODREJCP.NS":"Godrej Consumer",
    "GODFRYPHLP.NS":"Godfrey Phillips","GUJALKALI.NS":"Gujarat Alkalies","HINDUNILVR.NS":"Hindustan Unilever","ITC.NS":"ITC",
    "JKLAKSHMI.NS":"JK Lakshmi Cement","JKPAPER.NS":"JK Paper","JUBLFOOD.NS":"Jubilant FoodWorks","KAJARIACER.NS":"Kajaria Ceramics",
    "KPRMILL.NS":"KPR Mill","MARICO.NS":"Marico","NAVINFLUOR.NS":"Navin Fluorine","NESTLEIND.NS":"Nestle India",
    "PAGEIND.NS":"Page Industries","PCBL.NS":"PCBL","PIIND.NS":"PI Industries","RADICO.NS":"Radico Khaitan",
    "RAJESHEXPO.NS":"Rajesh Exports","RELAXO.NS":"Relaxo Footwears","SOLARINDS.NS":"Solar Industries","TATACHEM.NS":"Tata Chemicals",
    "TATACONSUM.NS":"Tata Consumer","UBL.NS":"United Breweries","VENKEYS.NS":"Venky's","ARVINDFASN.NS":"Arvind Fashions",
    "CANTABIL.NS":"Cantabil Retail","CENTURY.NS":"Century Textiles","DOLLAR.NS":"Dollar Industries","GOCOLORS.NS":"Go Colors",
    "KEWAL.NS":"Kewal Kiran","MANYAVAR.NS":"Vedant Fashions","PGEL.NS":"PG Electroplast","PRAJIND.NS":"Praj Industries",
    "RAYMOND.NS":"Raymond","SAPPHIRE.NS":"Sapphire Foods","SPENCERS.NS":"Spencer's Retail","TRENT.NS":"Trent",
    "VMART.NS":"V-Mart Retail","WONDERLA.NS":"Wonderla Holidays","BARBEQUE.NS":"Barbeque Nation","DEVYANI.NS":"Devyani International",
    "HATSUN.NS":"Hatsun Agro","APLAPOLLO.NS":"APL Apollo","ASTRAL.NS":"Astral Poly","CARYSIL.NS":"Carysil",
    "CASTROLIND.NS":"Castrol India","CENTURYPLY.NS":"Century Plyboards","CERA.NS":"Cera Sanitaryware","DEEPAKNTR.NS":"Deepak Nitrite",
    "ELECON.NS":"Elecon Engineering","FILATEX.NS":"Filatex India","FLUOROCHEM.NS":"Gujarat Fluorochemicals","GARFIBRES.NS":"Garware Technical",
    "GRINDWELL.NS":"Grindwell Norton","GSPL.NS":"Gujarat State Petronet","HIL.NS":"HIL Limited","INOXWIND.NS":"Inox Wind",
    "JINDALSAW.NS":"Jindal Saw","JKCEMENT.NS":"JK Cement","KALPATPOWR.NS":"Kalpataru Power","KANSAINER.NS":"Kansai Nerolac",
    "KCP.NS":"KCP Limited","KEC.NS":"KEC International","KEI.NS":"KEI Industries","KIRLOSENG.NS":"Kirloskar Oil",
    "LINDEINDIA.NS":"Linde India","MOIL.NS":"MOIL","NESCO.NS":"NESCO","NLCINDIA.NS":"NLC India",
    "PHILIPCARB.NS":"Phillips Carbon","PRINCEPIPE.NS":"Prince Pipes","PRSMJOHNSN.NS":"Prism Johnson","RAIN.NS":"Rain Industries",
    "RATNAMANI.NS":"Ratnamani Metals","RCF.NS":"Rashtriya Chemicals","RITES.NS":"RITES","RVNL.NS":"Rail Vikas Nigam",
    "SAIL.NS":"SAIL","SHREECEM.NS":"Shree Cement","SJVN.NS":"SJVN","SOBHA.NS":"Sobha",
    "SRF.NS":"SRF","STARCEMENT.NS":"Star Cement","SUMICHEM.NS":"Sumitomo Chemical","SUPREMEIND.NS":"Supreme Industries",
    "TECHNOE.NS":"Techno Electric","TIINDIA.NS":"Tube Investments","TIMETECHNO.NS":"Time Technoplast","TRITURBINE.NS":"Triveni Turbine",
    "UCOBANK.NS":"UCO Bank","UPL.NS":"UPL","VINATIORGA.NS":"Vinati Organics","WELCORP.NS":"Welspun Corp",
    "BEML.NS":"BEML","BDL.NS":"Bharat Dynamics","CARBORUNIV.NS":"Carborundum Universal","HAL.NS":"Hindustan Aeronautics",
    "KALYANI.NS":"Kalyani Forge","KIRLOSKAR.NS":"Kirloskar Brothers","SIEMENS.NS":"Siemens","THERMAX.NS":"Thermax",
    "AARTI.NS":"Aarti Industries","ALKYLAMINE.NS":"Alkyl Amines","ATUL.NS":"Atul Ltd","BASF.NS":"BASF India",
    "GNFC.NS":"GNFC","ADANIENSOL.NS":"Adani Energy","ADANIGAS.NS":"Adani Total Gas","ADANIGREEN.NS":"Adani Green",
    "AEGISCHEM.NS":"Aegis Logistics","BPCL.NS":"BPCL","GAIL.NS":"GAIL","GMRINFRA.NS":"GMR Infrastructure",
    "GSFC.NS":"GSFC","GUJGASLTD.NS":"Gujarat Gas","HINDPETRO.NS":"Hindustan Petroleum","IOC.NS":"Indian Oil",
    "IGL.NS":"Indraprastha Gas","MGL.NS":"Mahanagar Gas","ONGC.NS":"ONGC","OIL.NS":"Oil India",
    "PETRONET.NS":"Petronet LNG","RELIANCE.NS":"Reliance Industries","ADANIPOWER.NS":"Adani Power","ADANITRANS.NS":"Adani Transmission",
    "CESC.NS":"CESC","JSWENERGY.NS":"JSW Energy","NHPC.NS":"NHPC","NTPC.NS":"NTPC",
    "PFC.NS":"Power Finance Corp","POWERGRID.NS":"Power Grid","RECLTD.NS":"REC Limited","TATAPOWER.NS":"Tata Power",
    "TORNTPOWER.NS":"Torrent Power","SUZLON.NS":"Suzlon Energy","COALINDIA.NS":"Coal India","HINDALCO.NS":"Hindalco",
    "NMDC.NS":"NMDC","VEDL.NS":"Vedanta","CHAMBLFERT.NS":"Chambal Fertilizers","COROMANDEL.NS":"Coromandel International",
    "DEEPAKFERT.NS":"Deepak Fertilizers","FACT.NS":"FACT","NFL.NS":"National Fertilizers","ADANIPORTS.NS":"Adani Ports",
    "CONCOR.NS":"Container Corporation","IRCTC.NS":"IRCTC","ALLCARGO.NS":"Allcargo Logistics","BLUEDART.NS":"Blue Dart Express",
    "GATI.NS":"Gati","MAHLOG.NS":"Mahindra Logistics","TCI.NS":"Transport Corporation","TCIEXP.NS":"TCI Express",
    "VRL.NS":"VRL Logistics","MRPL.NS":"MRPL","DMART.NS":"Avenue Supermarts","FIVESTAR.NS":"Five Star Business",
    "DB.NS":"DB Corp","HATHWAY.NS":"Hathway Cable","INOXLEISUR.NS":"Inox Leisure","JAGRAN.NS":"Jagran Prakashan",
    "NETWORK18.NS":"Network18 Media","PVR.NS":"PVR Inox","PVRINOX.NS":"PVR Inox","SAREGAMA.NS":"Saregama India",
    "SUNTV.NS":"Sun TV Network","TIPS.NS":"Tips Industries","TV18BRDCST.NS":"TV18 Broadcast","TVTODAY.NS":"TV Today",
    "ZEEL.NS":"Zee Entertainment","HT.NS":"HT Media","NAVNETEDUL.NS":"Navneet Education","TREEHOUSE.NS":"Tree House Education",
    "DELTACORP.NS":"Delta Corp","ONMOBILE.NS":"OnMobile Global","AARTIIND.NS":"Aarti Industries","BHAGERIA.NS":"Bhageria Industries",
    "EXCEL.NS":"Excel Crop Care","HERANBA.NS":"Heranba Industries","INDOFIL.NS":"Indofil Industries","INSECTICIDES.NS":"Insecticides India",
    "NOCIL.NS":"NOCIL","RALLIS.NS":"Rallis India","SHARDACROP.NS":"Sharda Cropchem","ZUARI.NS":"Zuari Agro Chemicals",
    "BRIGADE.NS":"Brigade Enterprises","DLF.NS":"DLF","GODREJPROP.NS":"Godrej Properties","IBREALEST.NS":"Indiabulls Real Estate",
    "KOLTEPATIL.NS":"Kolte-Patil","LODHA.NS":"Macrotech Developers","MACROTECH.NS":"Macrotech Developers","OBEROIRLTY.NS":"Oberoi Realty",
    "PHOENIXLTD.NS":"Phoenix Mills","PRESTIGE.NS":"Prestige Estates","SIGNATURE.NS":"Signature Global","AHLUCONT.NS":"Ahluwalia Contracts",
    "ASHOKA.NS":"Ashoka Buildcon","HCC.NS":"Hindustan Construction","IRB.NS":"IRB Infrastructure","IRCON.NS":"IRCON International",
    "NBCC.NS":"NBCC India","NCCLTD.NS":"NCC Limited","PNCINFRA.NS":"PNC Infratech","ACC.NS":"ACC Cement",
    "AMBUJACEM.NS":"Ambuja Cements","DALMIACEM.NS":"Dalmia Bharat","GREENPLY.NS":"Greenply Industries","ORIENTCEM.NS":"Orient Cement",
    "RAMCOCEM.NS":"Ramco Cements","ULTRACEMCO.NS":"UltraTech Cement","HUDCO.NS":"HUDCO","SALASAR.NS":"Salasar Techno",
    "SUNFLAG.NS":"Sunflag Iron","CENTURYTEX.NS":"Century Textiles","CMSINFO.NS":"CMS Info Systems","ESABINDIA.NS":"ESAB India",
    "JWL.NS":"Jupiter Wagons"
}

SMALLCAP_STOCKS = {
    "AARTISURF.NS":"Aarti Surfactants","ABSORB.NS":"Absorb Plus","ACCELYA.NS":"Accelya Kale","ACRYSIL.NS":"Acrysil",
    "ADVENZYMES.NS":"Advanced Enzymes","AEROFLEX.NS":"Aeroflex Industries","AETHER.NS":"Aether Industries","AGCNET.NS":"AGC Networks",
    "AHLEAST.NS":"Asian Hotels East","AIIL.NS":"Ashapura Intimates","AIRAN.NS":"Airan Ltd","AKASH.NS":"Akash Infra-Projects",
    "AKSHARCHEM.NS":"Akshar Chem","ALKALI.NS":"Alkali Metals","ALPA.NS":"Alpa Laboratories","ALPHAGEO.NS":"Alphageo India",
    "ALPSINDUS.NS":"Alps Industries","AMIABLE.NS":"Amiable Logistics","AMJLAND.NS":"AMJ Land Holdings","AMRUTANJAN.NS":"Amrutanjan Health",
    "ANANTRAJ.NS":"Anant Raj","ANDHRSUGAR.NS":"Andhra Sugars","ANMOL.NS":"Anmol Industries","ANUP.NS":"Anupam Rasayan",
    "APARINDS.NS":"Apar Industries","APCL.NS":"Anjani Portland","APCOTEXIND.NS":"Apcotex Industries","APEX.NS":"Apex Frozen Foods",
    "APOLLO.NS":"Apollo Micro Systems","APTECHT.NS":"Aptech","ARASU.NS":"Arasu Cable","ARCHIDPLY.NS":"Archidply Industries",
    "ARCHIES.NS":"Archies Ltd","ARL.NS":"Apar Industries","ARMANFIN.NS":"Arman Financial","ARROWGREEN.NS":"Arrow Greentech",
    "ARSHIYA.NS":"Arshiya","ARTNIRMAN.NS":"Art Nirman","ASAHISONG.NS":"Asahi Songwon","ASAL.NS":"Automotive Stampings",
    "ASALCBR.NS":"Associated Alcohols","ASHIANA.NS":"Ashiana Housing","ASHIMASYN.NS":"Ashima Ltd","ASIANENE.NS":"Asian Energy Services",
    "ASIANHOTNR.NS":"Asian Hotels North","ASPINWALL.NS":"Aspinwall","ASTEC.NS":"Astec LifeSciences","ASTERDM.NS":"Aster DM Healthcare",
    "ASTRAMICRO.NS":"Astra Microwave","ATAM.NS":"Atam Valves","ATNINTER.NS":"ATN International","ATULAUTO.NS":"Atul Auto",
    "AURIONPRO.NS":"Aurionpro Solutions","AUSOMENT.NS":"Ausom Enterprise","AUSTRAL.NS":"Austral Coke","AUTOAXLES.NS":"Automotive Axles",
    "AUTOIND.NS":"Autoline Industries","AVALON.NS":"Avalon Technologies","AVTNPL.NS":"AVT Natural Products","AWL.NS":"Adani Wilmar",
    "AXISCADES.NS":"Axiscades Engineering","AXISGOLD.NS":"Axis Gold","AYMSYNTEX.NS":"AYM Syntex","AZAD.NS":"Azad Engineering",
    "BAGFILMS.NS":"BAG Films","BAJAJHIND.NS":"Bajaj Hindusthan Sugar","BALAJITELE.NS":"Balaji Telefilms","BALAXI.NS":"Balaxi Ventures",
    "BALKRISHNA.NS":"Balkrishna Paper","BALMLAWRIE.NS":"Balmer Lawrie","BALPHARMA.NS":"Bal Pharma","BANCOINDIA.NS":"Banco Products",
    "BANG.NS":"Bang Overseas","BANSWRAS.NS":"Banswara Syntex","BBOX.NS":"Black Box","BBL.NS":"Bharat Bijlee",
    "BBTC.NS":"Bombay Burmah","BCG.NS":"Brightcom Group","BCP.NS":"Banco Products","BEEKAY.NS":"Beekay Steel",
    "BEL.NS":"Bharat Electronics","BELSTAR.NS":"Belstar Microfinance","BEPL.NS":"Bhansali Engineering","BERGEPAINT.NS":"Berger Paints",
    "BFINVEST.NS":"BF Investment","BGRENERGY.NS":"BGR Energy Systems","BHAGYANGR.NS":"Bhagiradha Chemicals","BHANDARI.NS":"Bhandari Hosiery",
    "BHARATGEAR.NS":"Bharat Gears","BHARATWIRE.NS":"Bharat Wire Ropes","BHARTIARTL.NS":"Bharti Airtel","BHEL.NS":"BHEL",
    "BILENERGY.NS":"Bil Energy Systems","BIRLACABLE.NS":"Birla Cable","BIRLAMONEY.NS":"Aditya Birla Money","BIRLACORPN.NS":"Birla Corporation",
    "BIRLATYRE.NS":"Birla Tyres","BKM.NS":"Bkmindspace","BLACKROSE.NS":"Blackrose Industries","BLAL.NS":"BEML Land Assets",
    "BLKASHYAP.NS":"B L Kashyap","BLUEBLENDS.NS":"Blue Blends","BLUECOAST.NS":"Blue Coast Hotels","BLUEJET.NS":"Blue Jet Healthcare",
    "BODALCHEM.NS":"Bodal Chemicals","BOMDYEING.NS":"Bombay Dyeing","BOROLTD.NS":"Borosil Ltd","BRFL.NS":"Bombay Rayon",
    "BRO.NS":"Brigade Road","BSE.NS":"BSE Ltd","BSHSL.NS":"Bombay Super Hybrid","BSL.NS":"BSL Ltd",
    "BSOFT.NS":"Birlasoft","BTML.NS":"Bodal Trading","BURNPUR.NS":"Burnpur Cement","BUTTERFLY.NS":"Butterfly Gandhimathi",
    "CADSYS.NS":"Cadsys India","CALSOFT.NS":"California Software","CAMLINFINE.NS":"Camlin Fine Sciences","CANFINHOME.NS":"Can Fin Homes",
    "CAPF.NS":"Capital First","CAPTRUST.NS":"Capital Trust","CARERATING.NS":"CARE Ratings","CARGEN.NS":"Cargen Drugs",
    "CCCL.NS":"Consolidated Construction","CELEBRITY.NS":"Celebrity Fashions","CELLO.NS":"Cello World","CENTENKA.NS":"Century Enka",
    "CENTUM.NS":"Centum Electronics","CEREBRAINT.NS":"Cerebra Integrated","CGCL.NS":"Capri Global","CGPOWER.NS":"CG Power",
    "CHEMBOND.NS":"Chembond Chemicals","CHEMCON.NS":"Chemcon Speciality","CHEMFAB.NS":"Chemfab Alkalis","CHEMPLASTS.NS":"Chemplast Sanmar",
    "CHENNPETRO.NS":"Chennai Petroleum","CIEINDIA.NS":"CIE Automotive","CIGNITITEC.NS":"Cigniti Technologies","CINELINE.NS":"Cineline India",
    "CINEVISTA.NS":"Cinevista","CLNINDIA.NS":"Clariant Chemicals","CLSEL.NS":"Chaman Lal Setia","CMICABLES.NS":"CMI Ltd"
}

ALL_STOCKS = {**MIDCAP_STOCKS, **SMALLCAP_STOCKS}

INDUSTRY_BENCHMARKS = {
    'Technology': {'pe': 28, 'ev_ebitda': 16},'Financial Services': {'pe': 20, 'ev_ebitda': 14},'Consumer Cyclical': {'pe': 32, 'ev_ebitda': 16},
    'Consumer Defensive': {'pe': 38, 'ev_ebitda': 18},'Healthcare': {'pe': 30, 'ev_ebitda': 16},'Industrials': {'pe': 25, 'ev_ebitda': 14},
    'Energy': {'pe': 18, 'ev_ebitda': 10},'Basic Materials': {'pe': 20, 'ev_ebitda': 12},'Real Estate': {'pe': 28, 'ev_ebitda': 20},
    'Communication Services': {'pe': 22, 'ev_ebitda': 14},'Utilities': {'pe': 16, 'ev_ebitda': 12},'Default': {'pe': 22, 'ev_ebitda': 14}
}

def retry_with_backoff(retries=3, backoff_in_seconds=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        return None, str(e)[:100]
                    time.sleep(backoff_in_seconds * 2 ** x)
                    x += 1
        return wrapper
    return decorator

@st.cache_data(ttl=10800)
@retry_with_backoff(retries=3, backoff_in_seconds=2)
def fetch_stock_data(ticker):
    try:
        time.sleep(0.5)
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or len(info) < 5:
            return None, "No data"
        return info, None
    except Exception as e:
        return None, str(e)[:50]

def calculate_valuations(info):
    try:
        price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
        if not price or price <= 0:
            return None
        
        trailing_pe = info.get('trailingPE', 0)
        trailing_eps = info.get('trailingEps', 0)
        enterprise_value = info.get('enterpriseValue', 0)
        ebitda = info.get('ebitda', 0)
        market_cap = info.get('marketCap', 0)
        shares = info.get('sharesOutstanding', 1)
        sector = info.get('sector', 'Default')
        
        benchmark = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS['Default'])
        industry_pe = benchmark['pe']
        industry_ev_ebitda = benchmark['ev_ebitda']
        
        historical_pe = trailing_pe * 0.9 if trailing_pe and 0 < trailing_pe < 200 else industry_pe
        blended_pe = (industry_pe + historical_pe) / 2
        fair_value_pe = trailing_eps * blended_pe if trailing_eps and trailing_eps > 0 else None
        upside_pe = ((fair_value_pe - price) / price * 100) if fair_value_pe and price else None
        
        current_ev_ebitda = enterprise_value / ebitda if ebitda and ebitda > 0 else None
        target_ev_ebitda = (industry_ev_ebitda + current_ev_ebitda * 0.9) / 2 if current_ev_ebitda and 0 < current_ev_ebitda < 100 else industry_ev_ebitda
        
        if ebitda and ebitda > 0:
            fair_ev = ebitda * target_ev_ebitda
            net_debt = (info.get('totalDebt', 0) or 0) - (info.get('totalCash', 0) or 0)
            fair_mcap = fair_ev - net_debt
            fair_value_ev = fair_mcap / shares if shares else None
            upside_ev = ((fair_value_ev - price) / price * 100) if fair_value_ev and price else None
        else:
            fair_value_ev = None
            upside_ev = None
        
        ups = [v for v in [upside_pe, upside_ev] if v is not None]
        avg_upside = np.mean(ups) if ups else 0
        
        return {
            'ticker': info.get('symbol', 'N/A'),
            'company': info.get('longName', 'N/A'),
            'sector': sector,
            'price': round(price, 2),
            'trailing_pe': round(trailing_pe, 2) if trailing_pe and trailing_pe > 0 else None,
            'trailing_eps': round(trailing_eps, 2) if trailing_eps else None,
            'market_cap': market_cap,
            'fair_value_pe': round(fair_value_pe, 2) if fair_value_pe else None,
            'fair_value_ev': round(fair_value_ev, 2) if fair_value_ev else None,
            'upside_pe': round(upside_pe, 2) if upside_pe else None,
            'upside_ev': round(upside_ev, 2) if upside_ev else None,
            'avg_upside': round(avg_upside, 2),
            'industry_pe': industry_pe,
            'ebitda': ebitda
        }
    except:
        return None

def screen_stocks(tickers, max_stocks=100):
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = min(len(tickers), max_stocks)
    
    for idx, ticker in enumerate(list(tickers)[:max_stocks]):
        status_text.text(f"Analyzing {idx+1}/{total}: {ticker}")
        progress_bar.progress((idx + 1) / total)
        
        info, error = fetch_stock_data(ticker)
        if info and not error:
            vals = calculate_valuations(info)
            if vals:
                results.append(vals)
        
        time.sleep(0.3)
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)

def format_upside(val):
    if pd.isna(val):
        return "N/A"
    if val > 20:
        return f'<span class="positive">+{val:.1f}%</span>'
    elif val > 0:
        return f'<span class="neutral">+{val:.1f}%</span>'
    else:
        return f'<span class="negative">{val:.1f}%</span>'

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Screened Stocks')
    output.seek(0)
    return output

st.markdown('<div class="main-header"><h1>🔍 STOCK SCREENER</h1><p>1500+ Midcap & Smallcap Stocks | Advanced Filtering</p></div>', unsafe_allow_html=True)

if st.sidebar.button("Logout", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.header("📊 Screening Options")

screening_mode = st.sidebar.radio("Mode", ["Quick Screen (100 stocks)", "Full Screen (500 stocks)", "Custom Selection"])

if screening_mode == "Custom Selection":
    st.sidebar.subheader("Select Stocks")
    stock_type = st.sidebar.multiselect("Stock Type", ["Midcap", "Smallcap"], default=["Midcap", "Smallcap"])
    
    selected_stocks = {}
    if "Midcap" in stock_type:
        selected_stocks.update(MIDCAP_STOCKS)
    if "Smallcap" in stock_type:
        selected_stocks.update(SMALLCAP_STOCKS)
    
    num_stocks = st.sidebar.slider("Number of Stocks", 10, min(300, len(selected_stocks)), 50)
else:
    selected_stocks = ALL_STOCKS
    num_stocks = 100 if "Quick" in screening_mode else 500

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Filters")

min_upside = st.sidebar.slider("Minimum Upside %", -50, 100, 10)
max_pe = st.sidebar.slider("Maximum PE Ratio", 0, 100, 50)
min_price = st.sidebar.number_input("Minimum Price (Rs)", 0, 10000, 0)
max_price = st.sidebar.number_input("Maximum Price (Rs)", 0, 100000, 100000)

sector_filter = st.sidebar.multiselect("Sectors", list(INDUSTRY_BENCHMARKS.keys()), default=[])

if st.sidebar.button("🚀 START SCREENING", use_container_width=True, type="primary"):
    st.session_state.screening_done = False
    
    with st.spinner("🔍 Screening stocks... This may take a few minutes..."):
        df = screen_stocks(list(selected_stocks.keys()), num_stocks)
    
    if not df.empty:
        df_filtered = df[df['avg_upside'] >= min_upside]
        
        if max_pe > 0:
            df_filtered = df_filtered[(df_filtered['trailing_pe'].isna()) | (df_filtered['trailing_pe'] <= max_pe)]
        
        df_filtered = df_filtered[(df_filtered['price'] >= min_price) & (df_filtered['price'] <= max_price)]
        
        if sector_filter:
            df_filtered = df_filtered[df_filtered['sector'].isin(sector_filter)]
        
        df_filtered = df_filtered.sort_values('avg_upside', ascending=False)
        
        st.session_state.screened_df = df_filtered
        st.session_state.screening_done = True
    else:
        st.error("No data could be fetched. Try again later.")

if st.session_state.get('screening_done', False) and 'screened_df' in st.session_state:
    df = st.session_state.screened_df
    
    st.success(f"✅ Found {len(df)} stocks matching your criteria!")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>{len(df)}</h3><p>Total Stocks</p></div>', unsafe_allow_html=True)
    with col2:
        avg_upside = df['avg_upside'].mean()
        st.markdown(f'<div class="metric-card"><h3>{avg_upside:.1f}%</h3><p>Avg Upside</p></div>', unsafe_allow_html=True)
    with col3:
        undervalued = len(df[df['avg_upside'] > 20])
        st.markdown(f'<div class="metric-card"><h3>{undervalued}</h3><p>High Upside (>20%)</p></div>', unsafe_allow_html=True)
    with col4:
        strong_buy = len(df[df['avg_upside'] > 30])
        st.markdown(f'<div class="metric-card"><h3>{strong_buy}</h3><p>Strong Buy (>30%)</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📊 Top Opportunities", "📈 Charts & Analysis", "💾 Export Data"])
    
    with tab1:
        st.subheader("Top 20 Undervalued Stocks")
        
        display_df = df.head(20)[['ticker', 'company', 'sector', 'price', 'trailing_pe', 'avg_upside', 'fair_value_pe', 'market_cap']].copy()
        display_df['market_cap'] = display_df['market_cap'].apply(lambda x: f"₹{x/10000000:.0f} Cr" if pd.notna(x) else "N/A")
        display_df['avg_upside_formatted'] = display_df['avg_upside'].apply(format_upside)
        
        display_cols = display_df[['ticker', 'company', 'sector', 'price', 'trailing_pe', 'avg_upside_formatted', 'fair_value_pe', 'market_cap']]
        display_cols.columns = ['Ticker', 'Company', 'Sector', 'Price (₹)', 'PE Ratio', 'Upside %', 'Fair Value (₹)', 'Market Cap']
        
        st.markdown(display_cols.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        st.subheader("📋 Complete Results")
        st.dataframe(df, use_container_width=True, height=400)
    
    with tab2:
        st.subheader("Upside Distribution")
        
        fig1 = px.histogram(df, x='avg_upside', nbins=30, 
                           title='Distribution of Upside Potential',
                           labels={'avg_upside': 'Average Upside %'},
                           color_discrete_sequence=['#667eea'])
        st.plotly_chart(fig1, use_container_width=True)
        
        st.subheader("Sector-wise Analysis")
        
        sector_data = df.groupby('sector').agg({
            'avg_upside': 'mean',
            'ticker': 'count'
        }).reset_index()
        sector_data.columns = ['Sector', 'Avg Upside %', 'Count']
        sector_data = sector_data.sort_values('Avg Upside %', ascending=False)
        
        fig2 = px.bar(sector_data, x='Sector', y='Avg Upside %', 
                     title='Average Upside by Sector',
                     color='Avg Upside %',
                     color_continuous_scale='RdYlGn',
                     text='Count')
        st.plotly_chart(fig2, use_container_width=True)
        
        st.subheader("PE Ratio vs Upside")
        
        scatter_df = df[df['trailing_pe'].notna() & (df['trailing_pe'] > 0) & (df['trailing_pe'] < 100)]
        if not scatter_df.empty:
            fig3 = px.scatter(scatter_df, x='trailing_pe', y='avg_upside',
                            color='sector', size='market_cap',
                            hover_data=['company', 'price'],
                            title='PE Ratio vs Upside Potential',
                            labels={'trailing_pe': 'PE Ratio', 'avg_upside': 'Upside %'})
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Insufficient data for PE vs Upside chart")
        
        st.subheader("Price Range Distribution")
        
        price_ranges = pd.cut(df['price'], bins=[0, 100, 500, 1000, 5000, 100000], 
                             labels=['<100', '100-500', '500-1000', '1000-5000', '>5000'])
        price_dist = price_ranges.value_counts().reset_index()
        price_dist.columns = ['Price Range', 'Count']
        
        fig4 = px.pie(price_dist, values='Count', names='Price Range',
                     title='Stock Distribution by Price Range')
        st.plotly_chart(fig4, use_container_width=True)
    
    with tab3:
        st.subheader("📥 Download Screened Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv,
                file_name=f"stock_screener_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            excel_data = to_excel(df)
            st.download_button(
                label="📊 Download Excel",
                data=excel_data,
                file_name=f"stock_screener_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        st.markdown("---")
        st.subheader("📋 Custom Export Options")
        
        export_columns = st.multiselect(
            "Select columns to export",
            options=df.columns.tolist(),
            default=['ticker', 'company', 'sector', 'price', 'trailing_pe', 'avg_upside', 'fair_value_pe']
        )
        
        if export_columns:
            custom_df = df[export_columns]
            custom_csv = custom_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Custom CSV",
                data=custom_csv,
                file_name=f"custom_screener_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.markdown("---")
        st.info("""
        **Data Dictionary:**
        - **Ticker**: NSE stock symbol
        - **Company**: Company name
        - **Sector**: Industry sector
        - **Price**: Current market price
        - **PE Ratio**: Trailing PE ratio
        - **Upside %**: Average potential upside
        - **Fair Value**: Estimated fair value per share
        - **Market Cap**: Total market capitalization
        """)

else:
    st.info("👈 Configure your screening parameters in the sidebar and click 'START SCREENING'")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 How to Use:
        
        1. **Choose Screening Mode:**
           - Quick Screen: 100 stocks (2-3 mins)
           - Full Screen: 500 stocks (8-10 mins)
           - Custom: Select specific stocks
        
        2. **Set Your Filters:**
           - Minimum upside percentage
           - Maximum PE ratio
           - Price range
           - Preferred sectors
        
        3. **Start Screening:**
           - Click the button to begin
           - Wait for analysis to complete
           - Review top opportunities
        
        4. **Export Results:**
           - Download CSV or Excel
           - Custom column selection
           - Ready for further analysis
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Features:
        
        - **1500+ Stocks**: Complete midcap & smallcap coverage
        - **Smart Caching**: 3-hour data retention
        - **Dual Valuation**: PE + EV/EBITDA methods
        - **Advanced Filters**: Multi-criteria screening
        - **Visual Analytics**: Interactive charts
        - **Export Options**: CSV & Excel formats
        - **Sector Analysis**: Industry-wise breakdown
        - **Real-time Data**: Yahoo Finance integration
        """)
    
    st.markdown("---")
    
    st.warning("""
    **⚡ Important Notes:**
    
    - Screening takes 2-10 minutes depending on mode
    - Data is cached for 3 hours for faster re-screening
    - Rate limits: Wait 3-5 minutes if you hit limits
    - Best results during market hours (9:15 AM - 3:30 PM IST)
    - This is educational content, not investment advice
    """)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>NYZTrade Stock Screener | 1500+ Stocks | Educational Tool Only</div>", unsafe_allow_html=True)
