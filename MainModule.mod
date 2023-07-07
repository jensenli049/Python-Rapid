MODULE MainModule
    PERS wobjdata wA:=[FALSE,TRUE,"",[[-28.7515,-467.245,210.396],[0.895235,-0.0002283,0.000229099,-0.445595]],[[0,0,0],[1,0,0,0]]];
	PERS wobjdata wB:=[FALSE,TRUE,"",[[61.5836,-316.957,210.351],[1,-8.05716E-05,4.27909E-05,2.48885E-05]],[[0,0,0],[1,0,0,0]]];
	CONST robtarget screws_bin:=[[3.74,-0.45,-28.39],[0.000225507,-0.238536,-0.971134,-0.000356178],[-2,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
	CONST robtarget nuts_bin:=[[-0.24,0.71,-30.42],[0.000182474,-0.646312,-0.763073,-0.000195613],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget bolts_bin:=[[-0.24,0.71,-30.42],[0.000182474,-0.646312,-0.763073,-0.000195613],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
	!CONST robtarget intermediate:=[[29.14,-384.23,271.92],[0.000182163,-0.646284,-0.763097,-0.000124927],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]]; !safe point if needed
	CONST robtarget origin:=[[0,0,-30.42],[0.000211603,-0.646247,-0.763128,-0.000148896],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    PROC pick_and_place(robtarget pickup, robtarget place, pers wobjdata start, pers wobjdata end, num theta)
        !Reset Gripper; !make sure gripper is open
        Waittime(0.1); !wait time is to give gripper time to actuate
        MoveL Offs(pickup, 0, 0, 20), v100, fine, tool0\WObj:=start; !move to above pickup location to avoid crashing 
        MoveL RelTool (CRobT(), 0, 0, 0 \Rz:=theta), v100, fine, tool0\WObj:=start; !rotate tool by theta
        MoveL pickup, v100, fine, tool0\WObj:=start; !move down to pickup object
        !Set Gripper; !close gripper
        Waittime(0.1);
        MoveL Offs(pickup, 0, 0, 20), v100, fine, tool0\WObj:=start; !move back to above pickup location to avoid crashing
        !MoveL intermediate, v100, fine, tool0\WObj:=wobj0; !move to intermediate point (general safety code, unnecessary for same plane work objects)
        MoveL Offs(place, 0, 0, 20), v100, fine, tool0\WObj:=end; !move to above place location to avoid crashing 
        MoveL place, v100, fine, tool0\WObj:=end; !move down to place object
        !Reset Gripper; !open gripper
        Waittime(0.1);
        MoveL Offs(place, 0, 0, 20), v100, fine, tool0\WObj:=end; !move back to above place location to avoid crashing
        !MoveL intermediate, v100, fine, tool0\WObj:=wobj0; !move to intermediate point (general safety code, unnecessary for same plane work objects)
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
            MoveL origin, v100, fine, tool0\WObj:=wA; !move to origin (top left of frame), no fasteners in frame
        ENDTEST
    ENDPROC
    
    PROC socket_client() ! This Rapid Program is the client
        VAR bool tmp:=FALSE;
        VAR bool sorted:=FALSE;
        VAR string receive{5};
        VAR pos center:=[0,0,0];
        VAR num theta;
        SocketClose client_socket;
        SocketCreate client_socket; ! Initialize the port for this client to connect to the server

        SocketConnect client_socket, "192.168.0.170",4455 \Time:=10;!"127.0.0.1"
        WHILE NOT sorted DO
            SocketSend client_socket \Str:="Ready"; ! Tell server to send the next part location
            WaitTime(0.05);
            FOR iter FROM 1 TO 5 DO
                SocketReceive client_socket \Str:= receive{iter} \Time:= 15; !receive{1} = cx, receive{2} = cy, receive{3} = theta, receive{4} = fastener name
                TPWrite receive{iter}; ! Debugging: write received string to console
                IF receive{iter} = "Done" THEN !receive{5} = Done
                    RETURN;
                ENDIF
            ENDFOR
            tmp:=strtoval(receive{1}, center.x); ! Set center x coordinate to first received string
            tmp:=strtoval(receive{2}, center.y); ! Set center y coordinate to second received string
            tmp:=strtoval(receive{3}, theta); ! Set theta (degrees) to third received string
            determine_bin receive{4}, Offs(origin, center.x, center.y, center.z), Round(theta); ! Use function to determine where to drop off part
            IF receive{4} = "null" THEN !no more fasteners found
                sorted:=TRUE;
                SocketSend client_socket \Str:="Stop"; ! Tell server the program is over
            !ELSE
            !    SocketSend client_socket \Str:="Next"; ! Tell server to send the next part location
            ENDIF
            WaitTime(0.05);
            
        ENDWHILE
        Socketclose client_socket; 
    ENDPROC
    
    PROC main()
        socket_client;
        WaitTime(5);
    ENDPROC
ENDMODULE