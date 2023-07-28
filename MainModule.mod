MODULE MainModule
    PERS wobjdata wA:=[FALSE,TRUE,"",[[-28.7515,-467.245,210.396],[0.895235,-0.0002283,0.000229099,-0.445595]],[[0,0,0],[1,0,0,0]]]; !fix
	PERS wobjdata wB:=[FALSE,TRUE,"",[[127.42,357.551,140.657],[2.752E-06,2.13844E-05,-1,-3.63749E-05]],[[0,0,0],[1,0,0,0]]];
    CONST robtarget origin:=[[0,0,-30.42],[0.000211603,-0.646247,-0.763128,-0.000148896],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]]; !fix
	CONST robtarget screws_bin:=[[165.17,213.47,35.60],[0.943814,-0.0953691,0.0329916,0.314694],[1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
	CONST robtarget nuts_bin:=[[164.91,322.75,37.64],[0.609256,-0.181744,0.294421,0.713507],[1,0,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget bolts_bin:=[[170.31,117.14,35.60],[0.948673,-2.1255E-05,3.99746E-06,0.316259],[1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
	CONST robtarget intermediate:=[[116.30,399.87,158.62],[1.39043E-05,-0.316209,-0.94869,-8.1378E-05],[0,0,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS tooldata tGripper:=[TRUE,[[0,0,150],[1,0,0,0]],[1,[1,0,0],[1,0,0,0],0,0,0]];
    VAR socketdev client_socket;
    
    PROC pick_and_place(robtarget pickup, robtarget place, pers wobjdata start, pers wobjdata end, num theta)
        Reset Gripper; !make sure gripper is open
        Waittime(0.1); !wait time is to give gripper time to actuate
        MoveL Offs(pickup, 0, 0, 20), v100, fine, tGripper\WObj:=start; !move to above pickup location to avoid crashing 
        MoveL RelTool (CRobT(), 0, 0, 0 \Rz:=theta), v100, fine, tGripper\WObj:=start; !rotate tool by theta
        MoveL pickup, v100, fine, tGripper\WObj:=start; !move down to pickup object
        Set Gripper; !close gripper
        Waittime(0.1);
        MoveL Offs(pickup, 0, 0, 20), v100, fine, tGripper\WObj:=start; !move back to above pickup location to avoid crashing
        MoveL intermediate, v100, fine, tGripper\WObj:=wobj0; !move to intermediate point (general safety code, unnecessary for same plane work objects)
        MoveL Offs(place, 0, 0, 20), v100, fine, tGripper\WObj:=end; !move to above place location to avoid crashing 
        MoveL place, v100, fine, tGripper\WObj:=end; !move down to place object
        Reset Gripper; !open gripper
        Waittime(0.1);
        MoveL Offs(place, 0, 0, 20), v100, fine, tGripper\WObj:=end; !move back to above place location to avoid crashing
        MoveL intermediate, v100, fine, tGripper\WObj:=wobj0; !move to intermediate point (general safety code, unnecessary for same plane work objects)
    ENDPROC    
    
    PROC determine_bin(string fastener_type, robtarget pickup, num theta)
        TEST fastener_type
        CASE "screw":
            pick_and_place pickup, screws_bin, wA, wB, theta; !pick and place to screws bin
        CASE "nut":
            pick_and_place pickup, nuts_bin, wA, wB, theta; !pick and place to nuts bin
        CASE "bolt":
            pick_and_place pickup, bolts_bin, wA, wB, theta; !pick and place to bolts bin
        CASE "null":
            MoveL origin, v100, fine, tGripper\WObj:=wA; !move to origin (top left of frame), no fasteners in frame
        ENDTEST
    ENDPROC
    
    PROC socket_client() ! This Rapid Program is the client
        VAR bool tmp:=FALSE;
        VAR bool sorted:=FALSE;
        VAR string receive{5};
        VAR pos center:=[0,0,0];
        VAR num theta;
        SocketCreate client_socket; ! Initialize the port for this client to connect to the server

        SocketConnect client_socket, "129.21.61.21",4455 \Time:=10;!"127.0.0.1"192.168.0.170
        WHILE NOT sorted DO
            
            SocketSend client_socket \Str:="Ready"; ! Tell server to send the next part location
            WaitTime(.05);
            FOR iter FROM 1 TO 5 DO
                SocketReceive client_socket \Str:= receive{iter} \Time:=WAIT_MAX; !receive{1} = cx, receive{2} = cy, receive{3} = theta, receive{4} = fastener name
                TPWrite receive{iter}; ! Debugging: write received string to console
                IF receive{iter} = "Done" THEN !receive{5} = Done
                    !Socketclose client_socket;
                ENDIF
            ENDFOR
            tmp:=strtoval(receive{1}, center.x); ! Set center x coordinate to first received string
            tmp:=strtoval(receive{2}, center.y); ! Set center y coordinate to second received string
            tmp:=strtoval(receive{3}, theta); ! Set theta (degrees) to third received string
            determine_bin receive{4}, Offs(origin, center.x, center.y, center.z), Round(theta); ! Use function to determine where to drop off part
            IF receive{4} = "null" THEN !no more fasteners found
                sorted:=TRUE;
                TPWrite "null found";
                WaitTime(1);
            ELSE
                WaitTime(5);
            ENDIF
            WaitTime(.05);
        ENDWHILE
        SocketSend client_socket \Str:="Stop"; ! Tell server the program is over
        
        TPWrite "Stopping socket";
        Socketclose client_socket; 
        ERROR
        TPWrite "Error Message: " + NumtoStr(ERRNO,0);
            IF ERRNO=1095 THEN
                TPWrite "socket connection broken";
                SocketSend client_socket \Str:="Ready"; ! Tell server to send the next part location
                WaitTime(.1);
                RETRY;
            ENDIF
            IF ERRNO=ERR_SOCK_TIMEOUT THEN
                TPWrite "Socket Closed";
            ENDIF
    ENDPROC
    
    PROC main()
        socket_client;
        WaitTime(5);
        Stop;
    ENDPROC
ENDMODULE