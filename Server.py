from enlace import *
import time
import numpy as np
from datetime import datetime 

class Server:
    
    def __init__(self, img_location, TX, RX, baudrate, servidor, sensor):
        self.location_w  = img_location
        self.comTX       = TX
        self.comRX       = RX
        self.rxBuffer_H = 0
        self.rxBuffer = 0
        self.rxBuffer_resp = 0
        self.count = 1
        self.arquivo_recebido = bytearray()
        self.time_count = 0
        self.Baud_Rate = baudrate
        self.servidor = servidor
        self.sensor = sensor
        self.rxBuffer_copy = 0
    
    def package_analyzer(self,buffer, count, num_receive, sensor, servidor, temp_pl):
        
        try:
        
            type_pkg = False
            h0 = buffer[0]
            h1 = buffer[1]
            h2 = buffer[2]
            h3 = buffer[3]
            h4 = buffer[4]
            h5 = buffer[5]
            h6 = buffer[6]
            h7 = buffer[7]
            h8 = buffer[8]
            h9 = buffer[9]
            
            if (h5==114):
                payload_package = buffer[10:-4]
                if h5 == len(payload_package):
                    type_pkg = True
                
            else:
                payload_package = buffer[10:10+h5]
                extra_zero = buffer[10+h5:-4]  
                if 114==(len(payload_package)+len(extra_zero)):
                    type_pkg = True
                
            e1 = buffer[-4]
            e2 = buffer[-3]
            e3 = buffer[-2]
            e4 = buffer[-1]    
            
            if temp_pl == False:
                checking = count
            else:
                checking = count+1
            
            if (h0 == 3)and(h1 == sensor)and(h2 == servidor)and(h3 == num_receive)and(h4==checking)and(type_pkg==True)and(h8==0)and(h9==0)and(e1==255)and(e2==170)and(e3==255)and(e4==170):
                respost = "Tudo correto."
                return respost, h5 
            else:
                errormsg = "Ocorreu(eram) os seguinte(s) erros: "
                if (h0!= 3):
                    errormsg += "ID de Mensagem corrompida. "
                if (h1 != sensor):
                    errormsg += "Mensagem para outro sensor. "
                if (h2 != servidor):
                    errormsg += "Mensagem para outro servidor. "
                if (h3!=num_receive):
                    errormsg += "Quantidade total de pacotes incorreta no Head. "    
                if (h4 != count):
                    errormsg += "ID incorreto no Head. "
                if (type_pkg!=True):
                    errormsg += "Tamanho do Payload incorreto. "
                if ((e1!=255)or(e2!=170)or(e3!=255)or(e1!=170)):
                    errormsg += "Valor final incorreto."
                else:
                    errormsg += "Pacote corrompido."
                return errormsg, h5
        
        except:
            errormsg = "Pacote corrompido."
            h5 = 0
            return errormsg, h5
                
    
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

    def msg_analyzer(self,buffer):
        
        try:
            msg_package = buffer[0]
        
            if(msg_package==1):
                respost = "Handshake do client."
            elif(msg_package==3):
                respost = "Pacote recebido."
            elif(msg_package==5):
                respost = "Timeout do client."
            else:
                 respost = "Mensagem corrompida."
        except:
            respost = "Resposta não recebida."
        return respost    
    
    def handshake_analyzer(self,buffer,servidor,sensor):
        msg_rec = buffer[0]
        id_sensor = buffer[1]
        id_servidor = buffer[2]
        e1 = buffer[-4]
        e2 = buffer[-3]
        e3 = buffer[-2]
        e4 = buffer[-1]
        
        if (msg_rec==1)and(id_servidor==servidor)and(id_sensor==sensor)and(e1==255)and(e2==170)and(e3==255)and(e4==170):
            self.sensor = id_sensor
            self.servidor = id_servidor
            self.num_receive = buffer[3]
            self.id_arquivo = buffer[5]
            respost = "O Handshake do Client foi recebido corretamente."
            return respost 
        else:
            errormsg = "O Handshake do Client não foi recebido corretamente."   
            return errormsg
        
    def log_generator(self,typeof,msg):
        msg_type,total,current = self.buffer_values(msg)
        size = len(msg)
        time = datetime.now()
        timetxt = time.strftime("%d/%m/%Y %H:%M:%S")
        if (typeof=="recebido"):
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
            self.arch = "./log/server/server-log-"+timetxt+".txt"
            self.f = open(self.arch, "a")
            self.temp_pl = False
            
            print("-------------------------")
            print("Opening log archive")
            self.f.write("Server Started \n")
            
            print("-------------------------")
            print("Server Started")
            print("-------------------------")
            
            # Declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
            # para declarar esse objeto é o nome da porta.
            self.STX = enlace(self.comTX, self.Baud_Rate)
            self.SRX = enlace(self.comRX, self.Baud_Rate)
            
            # Ativa comunicacao. Inicia os threads e a comunicação serial 
            self.STX.enable()
            self.SRX.enable()
            self.count = 1
            
            # Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
            server_init_msg1 = "Server TX iniciado na porta: {}.".format(self.comTX)
            server_init_msg2 = "Server RX iniciado na porta: {}.".format(self.comRX)
            
            print(server_init_msg1)
            print(server_init_msg2) 
            print("-------------------------")
            
            # Local da imagem a ser salva
            server_init_msg3 = "Local onde a imagem recebida será salva: {}.".format(self.location_w)
            print(server_init_msg3)
            self.f.write(server_init_msg3+"\n")
            print("-------------------------")
            
            # Espera os dados do Header - Client
            server_init_msg4 = "Esperando o Handshake do Client."
            print(server_init_msg4)
            
            return([server_init_msg1,server_init_msg2,server_init_msg3,server_init_msg4])
        
        except Exception as erro:
            print("ops! :-\\")
            print(erro)
            self.STX.disable()
            self.SRX.disable()
            try:
                self.f.close()
            except:
                pass
                
    def handshake_receive_response(self):
        try:
            
            self.rxBuffer_H, nRx_H = self.SRX.getData(14,use_timeout=1)
            self.rxBuffer_H = bytearray(self.rxBuffer_H)
            server_comm_msg = self.handshake_analyzer(self.rxBuffer_H,self.servidor,self.sensor)
            print(server_comm_msg)
            print("-------------------------")
            
            return([server_comm_msg,self.num_receive])
        
        except Exception as erro:
            print("ops! :-\\")
            print(erro)
            self.STX.disable()
            self.SRX.disable()
            try:
                self.f.close()
            except:
                pass
                
    def execution_start(self):
        try:
            # Retornando uma resposta do Header para o Client
            server_time_msg = "Enviando uma resposta do Handshake para o Client."
            print(server_time_msg)
            init_pkg = self.package_modifier(self.rxBuffer_H,h0=2)
            self.STX.sendData(np.asarray(init_pkg))
            print("-------------------------")
            
            # Começar o cronometro do tempo de execução do envio
            server_time_msg2 = "Recebendo os pacotes do Client."
            print(server_time_msg2)
            print("-------------------------")
            
            return([server_time_msg,server_time_msg2])
            
        except Exception as erro:
            print("ops! :-\\")
            print(erro)
            self.CTX.disable()
            self.CRX.disable()
            try:
                self.f.close()
            except:
                pass             
                
    def data_receive_response(self, count):
        try: 
            check_var=True
            while (check_var==True):
                self.rxBuffer, nRx, self.time_count = self.SRX.getData(128,timeout=2,use_timeout=2,time_count=self.time_count)
                self.rxBuffer = bytearray(self.rxBuffer)
                if (len(self.rxBuffer)!=0):
                    self.log_generator("recebido",self.rxBuffer)  
                msg_check = self.msg_analyzer(self.rxBuffer)
                if (msg_check=="Pacote recebido."):
                    package_check, lenght_pkg = self.package_analyzer(self.rxBuffer, count, self.num_receive, self.sensor, self.servidor, self.temp_pl)
                    if (package_check=="Tudo correto."):
                        if (self.temp_pl==True):
                            self.temp_pl = False
                            count+=1 
                        self.f.write("Pacote recebido corretamente. \n")
                        server_data_msg1 = "Pacote recebido corretamente."
                        print(server_data_msg1)
                        server_data_msg2 = "Pacote atual: {} de {}.".format(count,self.num_receive)
                        print(server_data_msg2)
                        print("-------------------------")
                        self.time_count = 0
                        self.arquivo_recebido+=self.rxBuffer[10:10+lenght_pkg]
                        response_pkg = self.package_modifier(self.rxBuffer,h0=4,h7=1,remove_payload=1)
                        self.STX.sendData(np.asarray(response_pkg))
                        self.log_generator("enviado",response_pkg)
                        self.rxBuffer_copy = self.rxBuffer
                        check_var=False
                        self.temp_pl=True
                    else:
                        server_data_msg1 = package_check
                        self.f.write(server_data_msg1+" \n")
                        print(server_data_msg1)
                        server_data_msg2 = "Pacote atual: {} de {}.".format(count,self.num_receive)
                        print(server_data_msg2)
                        print("-------------------------")
                        response_pkg = self.package_modifier(self.rxBuffer,h0=6,h6=count,remove_payload=1)
                        self.STX.sendData(np.asarray(response_pkg))
                        self.log_generator("enviado",response_pkg)
                        check_var=False
                elif(msg_check=="Resposta não recebida."):
                    time.sleep(1) 
                    if (self.time_count==10):      
                        self.f.write("O sistema entrou em timeout. Abortando operação. \n")
                        server_data_msg1 = "Timed out."
                        print(server_data_msg1)
                        server_data_msg2 = "Comunicação encerrada com as portas {} e {}.".format(self.comTX,self.comRX)
                        print(server_data_msg2)
                        print("-------------------------")
                        self.STX.fisica.flush()
                        self.SRX.fisica.flush()
                        self.STX.disable()
                        self.SRX.disable()
                        self.f.close()
                        count=1000000000
                        return([server_data_msg1,server_data_msg2, count])
                    elif (self.time_count>=1):
                        #Enviar de novo, caso o client não recebeu a resposta
                        self.f.write("A resposta do Server não foi recebida. \n")
                        if (len(self.rxBuffer)>14):
                            response_pkg = self.package_modifier(self.rxBuffer,h0=4,h7=1,remove_payload=1) 
                            self.log_generator("enviado",response_pkg)
                        else:
                            response_pkg = self.package_modifier(self.rxBuffer_copy,h0=4,h7=1,remove_payload=1) 
                            self.log_generator("enviado",response_pkg)
                        self.STX.sendData(np.asarray(response_pkg))
                        server_data_msg1 = "Reenvio de resposta para o client."
                        print(server_data_msg1)
                        server_data_msg2 = "Pacote atual: {} de {}.".format(count,self.num_receive)
                        print(server_data_msg2)
                        print("-------------------------")
            
            return([server_data_msg1,server_data_msg2, count])
        
        except Exception as erro:
            print("ops! :-\\")
            print(erro)
            self.STX.disable()
            self.SRX.disable()
            try:
                self.f.close()
            except:
                pass
            return(["","", 1000000000])
    
    def execution_end(self):
        try:
            # Acesso aos bytes recebidos
            client_ex_msg1 = "Enviando a resposta de conclusão da conexão."
            print(client_ex_msg1)
            final_ack = self.package_modifier(self.rxBuffer_H,h0=2)
            self.STX.sendData(np.asarray(final_ack))
            
            return([client_ex_msg1])
            
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
            # Salva imagem
            print("-------------------------")
            self.f.write("Procedimento finalizado."+"\n")
            image_name = self.location_w.split("\\")
            server_end_msg1 = "Salvando dados no arquivo: {}.".format(image_name[1])
            self.f.write(server_end_msg1+"\n")
            print(server_end_msg1)
            fileimage = open(self.location_w, "wb")
            fileimage.write(self.arquivo_recebido)
            fileimage.close()
        
            # Encerra comunicação
            print("-------------------------")
            server_end_msg2 = "Comunicação encerrada com as portas {} e {}.".format(self.comTX,self.comRX)
            print(server_end_msg2)
            print("-------------------------")
            self.STX.fisica.flush()
            self.SRX.fisica.flush()
            self.STX.disable()
            self.SRX.disable() 
            try:
                self.f.close()
            except:
                pass
            
            return([server_end_msg1,server_end_msg2])
        
        except Exception as erro:
            print("ops! :-\\")
            print(erro)
            self.STX.disable()
            self.SRX.disable()
            try:
                self.f.close()
            except:
                pass