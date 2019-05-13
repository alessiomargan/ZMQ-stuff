#! /bin/sh

#ZPUB="alessio-IIT-lap.local:6666"
#ZPUB="amargan-desktop.local:6666"
#ZPUB="amargan-desktop.local:6666"
#ZPUB="10.255.32.91:5555"
#ZPUB="10.0.0.99:6666"
#ZPUB="pc104-alessio.local:6666"
#ZPUB="ccub-embedded.local:6666"
#ZPUB="ccub-deb-test.local:6666"
#ZPUB="carm-deb.local:6666"
#ZPUB="wheezy-i386-test.local:6668"
ZPUB="coman-linux.local:6668"


#std::vector<int> r_leg = {  4,  6,  7,  8,  9, 10};
#std::vector<int> l_leg = {  5, 11, 12, 13, 14, 15};
#std::vector<int> waist = {  1,  2, 3};
#std::vector<int> r_arm = { 16, 17, 18 ,19};
#std::vector<int> l_arm = { 20, 21, 22, 23};


MSG_ID="board_1,board_2,board_3"
#MSG_ID="board_17,board_21"
#MSG_ID="board_0,board_1,board_2,board_3"
#MSG_ID="pc104"

#SIGNALS="Piezo_out,Position,TT_2,TT_3"
SIGNALS="Position"
#SIGNALS="Position,Torque,Target_Pos,PID_out,PID_err"
#SIGNALS="sine,saw,square,triangle"
#SIGNALS="fx,fy,fz"
#SIGNALS="Position,"

python wx_mpl_dynamic_graph.py --zmq-pub tcp://$ZPUB  --zmq-msg-sub $MSG_ID --signals $SIGNALS --max-samples 5000 --draw-event-freq-ms 500 &

MSG_ID="board_2"
SIGNALS="Hip_pos"
python wx_mpl_dynamic_graph.py --zmq-pub tcp://$ZPUB  --zmq-msg-sub $MSG_ID --signals $SIGNALS --max-samples 4000 --draw-event-freq-ms 500 &

MSG_ID="board_2"
SIGNALS="Height"
python wx_mpl_dynamic_graph.py --zmq-pub tcp://$ZPUB  --zmq-msg-sub $MSG_ID --signals $SIGNALS --max-samples 4000 --draw-event-freq-ms 500 &


#MSG_ID="board_1"
MSG_ID="board_4,board_6,board_7,board_8,board_9,board_10"
SIGNALS="Torque"
#SIGNALS="Height"
#python wx_mpl_dynamic_graph.py --zmq-pub tcp://$ZPUB  --zmq-msg-sub $MSG_ID --signals $SIGNALS --max-samples 10000 --draw-event-freq-ms 500 &

MSG_ID="board_5,board_11,board_12,board_13,board_14,board_15"
SIGNALS="Torque"
#python wx_mpl_dynamic_graph.py --zmq-pub tcp://$ZPUB  --zmq-msg-sub $MSG_ID --signals $SIGNALS --max-samples 10000 --draw-event-freq-ms 500 &

MSG_ID="board_1,board_2,board_3"
SIGNALS="Torque"
python wx_mpl_dynamic_graph.py --zmq-pub tcp://$ZPUB  --zmq-msg-sub $MSG_ID --signals $SIGNALS --max-samples 5000 --draw-event-freq-ms 500 &


MSG_ID="board_16,board_17,board_18,board_19"
SIGNALS="Torque"
#python wx_mpl_dynamic_graph.py --zmq-pub tcp://$ZPUB  --zmq-msg-sub $MSG_ID --signals $SIGNALS --max-samples 5000 --draw-event-freq-ms 500 &

MSG_ID="board_20,board_21,board_22,board_23"
SIGNALS="Torque"
#python wx_mpl_dynamic_graph.py --zmq-pub tcp://$ZPUB  --zmq-msg-sub $MSG_ID --signals $SIGNALS --max-samples 5000 --draw-event-freq-ms 500 &
