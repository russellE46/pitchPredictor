import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

#Order based on:
#Count
#Hand
#CountHand
#PreviousPitch
#CountHandPreviousPitch

pitchTypes = ["4SFB", "SNK", "CUT", "CB/SCV/12-6CB/SCRB", "SL", "CH/SPL/FRK", "SLV", "KN"]

def create_pie_chart(title, data):
    """
    Create a pie chart from a dictionary using Matplotlib.

    Args:
        data_dict (dict): Dictionary where keys are labels and values are sizes of wedges.

    Returns:
        None
    """
    # Extract labels and sizes from the dictionary
    labels = []
    sizes = []
    total = 0
    for pair in data:
        total += pair[1]

    for pair in data:
        if pair[1] > 0:
            label = pair[0] + " | " + str(pair[1]) + " (" + str(round(float(pair[1])/float(total), 3) * 100) + "%)"
            labels.append(label)
            sizes.append(int(pair[1]))

    # Create the pie chart
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    ax1.set_title(title)
    # Show the plot
    return fig1

class situation:
    balls: int
    strikes: int
    hand:str
    prevPitch: str

    def __init__(self, ballz, strikez, hanD, pp):
        self.balls = ballz
        self.strikes = strikez
        self.hand = hanD
        self.prevPitch = pp

class pitch:
    pitchNo:int
    sit:situation
    cpType: str

    def __init__(self, pitchNum, sitch:situation, cp):
        self.pitchNo = pitchNum
        self.sit = sitch
        self.cpType = cp    

def incrementCount():
    if ballOrK:
        st.session_state.currStrikes += 1
        if st.session_state.currStrikes > 2:
            st.session_state.currStrikes = 0
            st.session_state.currBalls = 0

    else:
        st.session_state.currBalls += 1
        if st.session_state.currBalls > 3:
            st.session_state.strike = 0
            st.session_state.currBalls = 0

def processPitch(currPitch:pitch):
    count = (currPitch.sit.balls, currPitch.sit.strikes) 
    st.session_state.allPitches.append(currPitch)
    st.session_state.previousPitch = currPitch.cpType
    incrementCount()

    countMatchPitches = []
    leftPitches = []
    rightPitches = []
    prevPitchMatchPitches = []

    #get pitches that match current situation
    for p in st.session_state.allPitches:
        #aggregate account matches
        countMatch = p.sit.balls == st.session_state.currBalls and p.sit.strikes == st.session_state.currStrikes
        if countMatch:
            countMatchPitches.append(p)

        #aggregate handed pitches
        if p.sit.hand == "Left":
            leftPitches.append(p)

        if p.sit.hand == "Right":
            rightPitches.append(p)

        #prevPitchRanks
        if p.sit.prevPitch == currPitch.cpType:
            prevPitchMatchPitches.append(p)

    #initialize datasets for output
    st.session_state.output["countRanks"] = {} #
    st.session_state.output["leftRanks"] = {} #
    st.session_state.output["rightRanks"] = {} #
    st.session_state.output["prevPitchRanks"] = {} #
    st.session_state.output["countLeftRanks"] = {} #
    st.session_state.output["countRightRanks"] = {} #
    st.session_state.output["countPrevPitchRanks"] = {} #
    st.session_state.output["leftPrevPitchRanks"] = {} #
    st.session_state.output["rightPrevPitchRanks"] = {} #
    st.session_state.output["countLeftPrevPitchRanks"] = {} #
    st.session_state.output["countRightPrevPitchRanks"] = {} #
    for pType in pitchTypes:
        for dataset in st.session_state.output.keys():
             st.session_state.output[dataset][pType] = 0

    #count data
    for cp in countMatchPitches:
        st.session_state.output["countRanks"][cp.cpType] += 1
        if cp in leftPitches:
            st.session_state.output["countLeftRanks"][cp.cpType] += 1
            if cp in prevPitchMatchPitches:
                st.session_state.output["countLeftPrevPitchRanks"][cp.cpType] += 1
        elif cp in rightPitches:
            st.session_state.output["countRightRanks"][cp.cpType] += 1
            if cp in prevPitchMatchPitches:
                st.session_state.output["countRightPrevPitchRanks"][cp.cpType] += 1

        if cp in prevPitchMatchPitches:
            st.session_state.output["countPrevPitchRanks"][cp.cpType] += 1

    for pp in prevPitchMatchPitches:
        st.session_state.output["prevPitchRanks"][pp.cpType] += 1
        if pp in leftPitches:
            st.session_state.output["leftPrevPitchRanks"][pp.cpType] += 1
        if pp in rightPitches:
            st.session_state.output["rightPrevPitchRanks"][pp.cpType] += 1

    for lp in leftPitches:
        st.session_state.output["leftRanks"][lp.cpType] += 1        

    for rp in rightPitches:
        st.session_state.output["rightRanks"][rp.cpType] += 1
        
    #sort data descending
    for dataset in st.session_state.output.keys():
        st.session_state.output[dataset] = sorted(st.session_state.output[dataset].items(), key=lambda x:x[1], reverse=True)


if "allPitches" not in st.session_state:
    print("creating data")
    st.session_state["allPitches"] = []
    st.session_state.output = {}

st.sidebar.title("PitchPredictorX")
st.sidebar.title("Batter Hand: ")
handedness = st.sidebar.select_slider(label = "Left/Right", options=["Left", "Right"], value="Right")

if "pitchCount" not in st.session_state:
    st.session_state["pitchCount"] = 0
    st.session_state["currBalls"] = 0
    st.session_state["currStrikes"] = 0
    st.session_state["previousPitch"] = "None"

with st.sidebar:
    st.title("Count: " + str(st.session_state.currBalls) + "-" + str(st.session_state.currStrikes))
    ballOrK = st.toggle(label="Ball/Strike")
    with st.container(height = 240):
        col1, col2 = st.columns([1,2.5])

    pButtonClickedArr = []
    for i, availPitch in enumerate(pitchTypes):
        if i % 2 == 0:
            with col1:
                pButtonClicked = False
                sit = situation(st.session_state.currBalls, st.session_state.currStrikes,handedness, st.session_state.previousPitch)
                currPitch = pitch(st.session_state.pitchCount, sit, availPitch)
                pButtonClicked = st.button(label=availPitch, on_click=processPitch, args=((currPitch,)))
                pButtonClickedArr.append(pButtonClicked)
        if i % 2 == 1:
            with col2:
                pButtonClicked = False
                sit = situation(st.session_state.currBalls, st.session_state.currStrikes,handedness, st.session_state.previousPitch)
                currPitch = pitch(st.session_state.pitchCount, sit, availPitch)
                pButtonClicked = st.button(label=availPitch, on_click=processPitch, args=((currPitch,)))
                pButtonClickedArr.append(pButtonClicked)

    newAB = st.button(label="New AB")
    if newAB:
        st.session_state.strike = 0
        st.session_state.currBalls = 0

gCol1, gcol2 = st.columns([1,1])

countStr = "Count: " + str(st.session_state.currBalls) + "-" + str(st.session_state.currStrikes)
prevPitchStr = "After " + st.session_state.previousPitch + ":"
dataTitles = {"countRanks":countStr,
              "leftRanks": "To LHB: ",
              "rightRanks": "To RHB: ",
              "prevPitchRanks": prevPitchStr,
              "countLeftRanks": countStr + " to LHB: ",
              "countRightRanks": countStr + " to RHB: ",
              "countPrevPitchRanks": countStr + " " + prevPitchStr,
              "leftPrevPitchRanks": "To LHB " + prevPitchStr,
              "rightPrevPitchRanks": "To RHB " + prevPitchStr,
              "countLeftPrevPitchRanks": countStr + " to LHB " + prevPitchStr,
              "countRightPrevPitchRanks": countStr + " to RHB " + prevPitchStr}

graphsPrinted = 0
if not st.session_state.output.keys():
    st.title("No data yet")

else:
    for stat in st.session_state.output.keys():
        if handedness == "Left":
            if stat.find("right") != -1 or stat.find("Right") != -1:
                continue
        elif handedness == "Right":
            if stat.find("left") != -1 or stat.find("Left") != -1:
                continue

        empty = True
        oList = st.session_state.output[stat]
        for p in oList:
            if p[1] > 0:
                empty = False

        if not empty:
            pie = create_pie_chart(dataTitles[stat], st.session_state.output[stat])
            st.pyplot(pie)
            # if graphsPrinted % 2 == 0:
            #     with gCol1:
            #         with st.container(height = 275):
            #             st.pyplot(pie)
            # if graphsPrinted % 2 == 1:
            #     with gcol2:
            #         with st.container(height = 275):
            #             st.pyplot(pie)
            graphsPrinted += 1

if (True in pButtonClickedArr) or newAB:
    st.rerun()