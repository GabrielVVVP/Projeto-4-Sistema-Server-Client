from enlace import *
import time
import numpy as np
import sys
import random
from datetime import datetime

class Client:
    
    def __init__(self, img_location, TX, RX, baudrate,client,sensor):
        self.location_r  = img_location
        self.comTX       = TX
        self.comRX       = RX
        self.txBuffer = 0
        self.txBuffer_len = 0
        self.rxBuffer_H = 0
        self.rxBuffer_D = 0
        self.count = 1
        self.numberofpackages = 0
        self.start_time = 0
        self.execution_time = 0
        self.time_count = 0
        self.Baud_Rate = baudrate
        self.client = client
        self.sensor= sensor
        
    def package_analyzer(self,buffer):

        try:
            msg_package = buffer[0]
            if(msg_package==2):
                respost = "Recebido do Server a resposta do handshake corretamente."
            elif(msg_package==4):
                ultimo_corr = buffer[7]
                if (ultimo_corr==1):
                    respost = "Tudo correto."
                else:
                    respost = "Tudo correto."
            elif(msg_package==6):
                reenvio = buffer[6]
                if (reenvio!=0):
                    respost = "Erro no pacote, o pacote será reenviado."
                else:
                    respost = "Byte h6 corrompido."
            else:
                respost = "Byte h0 corrompido."
        except:
            respost = "Falha no recebimento da resposta."
        
        return respost    
    
    def package_builder(self,Buffer, id_sensor, id_servidor, id_arquivo):   
        # Calculando o número de Pacotes
        packages_to_send = []
        
        Buffer_len = len(Buffer)
        
        finalpackage_size = (Buffer_len)%114
        
        if (finalpackage_size != 0):
            numberofpackages = (Buffer_len//114)+1
        else:
            numberofpackages = (Buffer_len//114)
            
        # Criando os pacotes e organizando
        for i in range(0,numberofpackages+1):
            
            if (i==0):
                # head
                h0 = (1).to_bytes(1, byteorder="big")
                h1 = (id_sensor).to_bytes(1, byteorder="big")
                h2 = (id_servidor).to_bytes(1, byteorder="big")
                h3 = (numberofpackages).to_bytes(1, byteorder="big")
                h4 = (i).to_bytes(1, byteorder="big")
                h5 = (id_arquivo).to_bytes(1, byteorder="big")
                h6 = (0).to_bytes(1, byteorder="big")
                h7 = (0).to_bytes(1, byteorder="big")
                h8 = (0).to_bytes(1, byteorder="big")
                h9 = (0).to_bytes(1, byteorder="big")
                
            else:    
            
                # Payload
                if ((Buffer_len>114)and(finalpackage_size!=0)):
                    extra_part = (0).to_bytes(114-finalpackage_size, byteorder="big")
                    if (i < numberofpackages):
                        payload_package = Buffer[114*(i-1):i*114]
                        pkg_size = 114
                    else:
                        payload_package = Buffer[114*(i-1):(114*(i-1)+finalpackage_size)]+extra_part
                        pkg_size = finalpackage_size
                elif ((Buffer_len>114)and(finalpackage_size==0)):
                    if (i < numberofpackages):
                        payload_package = Buffer[114*(i-1):i*114]
                    else:
                        payload_package = Buffer[114*(i-1):(114*(i-1)+114)] 
                    pkg_size = 114    
                else:
                    extra_part = (0).to_bytes(114-finalpackage_size, byteorder="big")
                    payload_package = Buffer[0:finalpackage_size]+extra_part
                    pkg_size = finalpackage_size
                
                # head
                h0 = (3).to_bytes(1, byteorder="big")
                h1 = (id_sensor).to_bytes(1, byteorder="big")
                h2 = (id_servidor).to_bytes(1, byteorder="big")
                h3 = (numberofpackages).to_bytes(1, byteorder="big")
                h4 = (i).to_bytes(1, byteorder="big")
                h5 = (pkg_size).to_bytes(1, byteorder="big")
                h6 = (0).to_bytes(1, byteorder="big")
                h7 = (0).to_bytes(1, byteorder="big")
                h8 = (0).to_bytes(1, byteorder="big")
                h9 = (0).to_bytes(1, byteorder="big")    
            
            head = h0+h1+h2+h3+h4+h5+h6+h7+h8+h9
            
            # EOL
            end_package1 = (255).to_bytes(1, byteorder="big")
            end_package2 = (170).to_bytes(1, byteorder="big")
            end_package = end_package1+end_package2+end_package1+end_package2
            
            # Assemble
            if (i==0):
                package = head+end_package
            else:    
                package = head+payload_package+end_package
            
            packages_to_send.append(package)
            
        return packages_to_send, numberofpackages, Buffer_len

    def package_modifier(self,package,h0=0,h1=0,h2=0,h3=0,h4=0,h5=0,h6=0,h7=0,h8=0,h9=0,remove_payload=0):
        
        if (remove_payload==1):
            package = package[0:10] + package[-4:] 
        
        if (h0!=0):
            temp = (h0).to_bytes(1, byteorder="big")
            package = temp+package[1:]
        if (h1!=0):
            temp = (h1).to_bytes(1, byteorder="big")
            package = package[0]+temp+package[2:]
        if (h2!=0):
            temp = (h2).to_bytes(1, byteorder="big")
            package = package[:2]+temp+package[3:]
        if (h3!=0):
            temp = (h3).to_bytes(1, byteorder="big")  
            package = package[:3]+temp+package[4:]
        if (h4!=0):
            temp = (h4).to_bytes(1, byteorder="big") 
            package = package[:4]+temp+package[5:]
        if (h5!=0):
            temp = (h5).to_bytes(1, byteorder="big")
            package = package[:5]+temp+package[6:]
        if (h6!=0):
            temp = (h6).to_bytes(1, byteorder="big")
            package = package[:6]+temp+package[7:]
        if (h7!=0):
            temp = (h7).to_bytes(1, byteorder="big")
            package = package[:7]+temp+package[8:]
        if (h8!=0):
            temp = (h8).to_bytes(1, byteorder="big")
            package = package[:8]+temp+package[9]
        if (h9!=0):
            temp = (h9).to_bytes(1, byteorder="big")
            package = package[:9]+temp  
    
        package = bytearray(package)     
        
        return package
    
    def acknowledge_analyzer(self,buffer,buffer2):
    
        if (buffer==buffer2):
            respost = "Recebido do Server a resposta do Acknowledge corretamente."
            return respost 
        else:
            errormsg = "O Acknowledge do Server não foi recebido corretamente."   
            return errormsg
        
    def package_errors(self,buffer,force_errors=0):
        # Force Errors
        if(force_errors==1):
            id_value = buffer[4]
            id_value+=1
            id_val = (id_value).to_bytes(1, byteorder="big")
            buffer = buffer[:4]+id_val+buffer[5:]
        elif(force_errors==2):
            quantity_value = buffer[3]
            quantity_value+=1
            q_val = (quantity_value).to_bytes(1, byteorder="big")
            buffer = buffer[:3]+q_val+buffer[4:]
        elif(force_errors==3):
            size_value = buffer[5]
            size_value+=1
            s_val = (size_value).to_bytes(1, byteorder="big")
            buffer = buffer[:5]+s_val+buffer[6:]
        elif(force_errors==4):
            wrong_end = (203).to_bytes(1, byteorder="big")
            buffer = buffer[:-1]+wrong_end
        return buffer    
    
    def log_generator(self,typeof,msg):
        msg_type,total,current = self.buffer_values(msg)
        size = len(msg)
        time = datetime.now()
        timetxt = time.strftime("%d/%m/%Y %H:%M:%S")
        if (typeof=="enviado"):
            string_log = timetxt+" / "+typeof+" / "+str(msg_type)+" / "+str(size)+" / "+str(current)+" / "+str(total)+" \n"
        else:
            string_log = timetxt+" / "+typeof+" / "+str(msg_type)+" / "+str(size)+" \n"
        self.f.write(string_log)
            
    def buffer_values(self,msg):
        msg_type = msg[0]
        total = msg[3]
        current = msg[4]
        return msg_type,total,current
        
        
    def init_comm(self):
        try:
            time = datetime.now()
            timetxt = time.strftime("date_%d-%m-%Y-time_%H-%M-%S")
            self.arch = "./log/client/client-log-"+timetxt+".txt"
            self.f = open(self.arch, "a")
            
            print("-------------------------")
            print("Opening log archive")
            self.f.write("Client Started \n")
            
            
            print("-------------------------")
            print("Client Started")
            print("-------------------------")
            
            # Declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
            # para declarar esse objeto é o nome da porta.
            self.CTX = enlace(self.comTX, self.Baud_Rate)
            self.CRX = enlace(self.comRX, self.Baud_Rate)
            
            # Ativa comunicacao. Inicia os threads e a comunicação serial 
            self.CTX.enable()
            self.CRX.enable()
            self.count = 1
            self.flux_again = 0
            
            # Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
            client_init_msg1 = "Client TX iniciado na porta: {}.".format(self.comTX)
            client_init_msg2 = "Client RX iniciado na porta: {}.".format(self.comRX)
            
            print(client_init_msg1)
            print(client_init_msg2)  
            print("-------------------------")
            
            # Carregando imagem a ser executada
            image_name = self.location_r.split("\\")
            self.txBuffer = open(self.location_r, "rb").read()
            self.txBuffer_len = len(self.txBuffer)
            client_init_msg3 = "Imagem para transmissão: {} ({} bytes).".format(image_name[1], self.txBuffer_len)
            print(client_init_msg3)
            self.f.write(client_init_msg3+"\n")
            print("-------------------------")
            
            # Criando os pacotes do sistema
            client_init_msg4 = "Criando os pacotes do sistema."
            print(client_init_msg4)
            print("-------------------------")
            self.pacotes, self.numberofpackages, self.size = self.package_builder(self.txBuffer,self.sensor,self.client,1)
            
            return([client_init_msg1,client_init_msg2,client_init_msg3,client_init_msg4, self.numberofpackages])
        
        except Exception as erro:
            print("ops! :-\\")
            print(erro)
            self.CTX.disable()
            self.CRX.disable()
            try:
                self.f.close()
            except:
                pass
            return(["","", 1000000000])
                
    def handshake_send_response(self):
        try:
            # Enviando para o Server o Header
            client_comm_msg1 = "Enviando para o Server o Handshake."
            self.f.write("Enviando para o Server o Handshake. \n")
            print(client_comm_msg1)
            print("-------------------------")
            self.CTX.sendData(np.asarray(self.pacotes[0])) 
            
            # Recebendo uma resposta do Server sobre o Handshake
            client_comm_msg2 = "Esperando a resposta do Server sobre o Handshake."
            print(client_comm_msg2)
            self.rxBuffer_H, nRx = self.CRX.getData(14, timeout=20)
            self.rxBuffer_H = bytearray(self.rxBuffer_H)
            client_comm_msg3 = self.package_analyzer(self.rxBuffer_H)
            if (client_comm_msg3=="Recebido do Server a resposta do handshake corretamente."):
                self.f.write("Recebido do Server a resposta do handshake corretamente. \n")
            elif (client_comm_msg3=="Falha no recebimento da resposta."):
                self.f.write("O handshake não foi enviado corretamente e retornou timeout de 20 segundos. \n")
            else:
                self.f.write("A resposta do handshake foi recebida com erros. \n")
            print(client_comm_msg3)
            print("-------------------------")
            
            return([client_comm_msg1,client_comm_msg2,client_comm_msg3])
        
        except Exception as erro:
            print("ops! :-\\")
            print(erro)
            self.CTX.disable()
            self.CRX.disable()
            try:
                self.f.close()
            except:
                pass
    
    def execution_start(self):
        try:
            # Começar o cronometro do tempo de execução do envio
            client_time_msg1 = "Iniciando o timer de execução."
            print(client_time_msg1)
            self.start_time = time.time()
            
            client_time_msg2 = "Iniciando envio de pacotes."
            print(client_time_msg2)
            print("-------------------------")
            
            return([client_time_msg1,client_time_msg2])
            
        except Exception as erro:
            print("ops! :-\\")
            print(erro)
            self.CTX.disable()
            self.CRX.disable()  
            try:
                self.f.close()
            except:
                pass
                
    def data_send_response(self, count):
        try:
            my_errors = [0,1,2,3,4]
            error_value = random.choices(my_errors, weights = [100,0,0,0,0])[0]
            transmission_stop = [0,10,20]
            trans_num = random.choices(transmission_stop, weights = [100,0,0])[0]
            self.pacote = self.pacotes[count]
            self.txBuffer_S = self.package_errors(self.pacote,error_value)
            self.CTX.sendData(np.asarray(self.txBuffer_S))
            if (len(self.txBuffer_S)!=0):
                self.log_generator("enviado",self.txBuffer_S)
            time.sleep(trans_num)
            if (trans_num!=0)or(self.flux_again==1):
                self.CRX.fisica.flush()
                self.CTX.disable()
                self.CTX.enable()
                self.flux_again+= 1
                if (self.flux_again==2):
                    self.flux_again=0
            self.rxBuffer_D, nRx, self.time_count = self.CRX.getData(14,use_timeout=2,time_count=self.time_count)
            self.rxBuffer_D = bytearray(self.rxBuffer_D)
            package_check = self.package_analyzer(self.rxBuffer_D)
            if (len(self.rxBuffer_D)!=0):
                self.log_generator("recebido",self.rxBuffer_D)   
            if (package_check=="Tudo correto."):
                self.f.write("Pacote recebido corretamente. \n")
                client_data_msg1 = "Pacote enviado corretamente."
                print(client_data_msg1)
                client_data_msg2 = "Pacote atual: {} de {}.".format(count,self.numberofpackages)
                print(client_data_msg2)
                count+=1
                self.time_count = 0
            else:
                client_data_msg1 = package_check
                print(client_data_msg1)
                client_data_msg2 = "Pacote atual: {} de {}.".format(count,self.numberofpackages)
                print(client_data_msg2)
                if (self.time_count>=4):
                    self.f.write("O sistema entrou em timeout. Abortando operação. \n")
                    current_pkg = self.package_modifier(self.pacotes[count],h0=5,remove_payload=1)
                    self.CTX.sendData(np.asarray(current_pkg))
                    client_data_msg1 = "Timed out."
                    print(client_data_msg1)
                    print("-------------------------")
                    client_data_msg2 = "Comunicação encerrada com as portas {} e {}.".format(self.comTX,self.comRX)
                    print(client_data_msg2)
                    self.CTX.fisica.flush()
                    self.CRX.fisica.flush()
                    self.CTX.disable()
                    self.CRX.disable()
                    self.f.close()
                    count=1000000000
                elif (package_check=="Erro no pacote, o pacote será reenviado."):
                    self.f.write("Erro no pacote recebido. \n")
                    
                elif (self.time_count>=1):
                    self.f.write("A resposta do Server não foi recebida. \n")
                    client_data_msg1 = "Timer de reenvio excedido. Reenviando o pacote."
                    print(client_data_msg1)
                
            print("-------------------------")               
                              
            return([client_data_msg1,client_data_msg2,count])
        
        except Exception as erro:
            print("ops! :-\\")
            print(erro)
            self.CTX.disable()
            self.CRX.disable()
            try:
                self.f.close()
            except:
                pass
    
    def execution_end(self):
        try:
            # Acesso aos bytes recebidos
            client_ex_msg1 = "Esperando a resposta de conclusão da conexão."
            print(client_ex_msg1)
            self.rxBuffer_A, nRx = self.CRX.getData(14)
            self.rxBuffer_A = bytearray(self.rxBuffer_A)
            
            package_check = self.acknowledge_analyzer(self.rxBuffer_H, self.rxBuffer_A)
            
            if (package_check == "Recebido do Server a resposta do Acknowledge corretamente."):
                client_ex_msg2 = "O arquivo inteiro foi enviado corretamente."
            else:
                client_ex_msg2 = "O arquivo inteiro não foi enviado corretamente."
            
            print(client_ex_msg2)
            print("-------------------------")         
            
            return([client_ex_msg1,client_ex_msg2])
            
        except Exception as erro:
            print("ops! :-\\")
            print(erro)
            self.CTX.disable()
            self.CRX.disable()
            try:
                self.f.close()
            except:
                pass            
                
    def end_connection(self):
        try:
            client_end_msg1 = "Concluindo a conexão com o Server."
            print(client_end_msg1)
            print("-------------------------")
            
            # Encerra tempo de cronometro
            print("Procedimento finalizado")
            self.f.write("Procedimento finalizado."+"\n")
            self.execution_time = time.time() - self.start_time
            client_end_msg2 = "Tempo de execução: {:.2f} segundos.".format(self.execution_time)
            print(client_end_msg2)
            client_end_msg3 = "Velocidade de transmissão: {:.2f} Bytes/segundos.".format(self.txBuffer_len/self.execution_time)
            print(client_end_msg3)
            self.f.write(client_end_msg2+"\n")
            self.f.write(client_end_msg3+"\n")
            
            # Encerra comunicação
            print("-------------------------")
            client_end_msg4 = "Comunicação encerrada com as portas {} e {}.".format(self.comTX,self.comRX)
            print(client_end_msg4)
            print("-------------------------")
            self.CTX.fisica.flush()
            self.CRX.fisica.flush()
            self.CTX.disable()
            self.CRX.disable()
            try:
                self.f.close()
            except:
                pass
            
            return([client_end_msg1,client_end_msg2,client_end_msg3,client_end_msg4])
        
        except Exception as erro:
            print("ops! :-\\")
            print(erro)
            self.CTX.disable()
            self.CRX.disable()
            try:
                self.f.close()
            except:
                pass