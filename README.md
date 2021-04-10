# Projeto 4 - Sistema Server-Client

Na pasta de Logs, terá os 4 logs listados pela entrega, com a exceção da transmissão 5 com falha física, devido a natureza simulada deste projeto.

Assim:

Client e Server 1 = Descrevem o funcionamento normal do sistema, com transmissão completamente funcional.

Client e Server 2 = Erro no id do pacote, que é reinviado e consegue completar a transmissão completamente funcional.

Client e Server 3 = O Client envia a resposta do handshake antes do Server ser ativado. Assim, após não conseguir enviar o Handshake para o Server, um botão de "Reenviar Handshake" aparecerá na tela do Client. Desta vez, o Server está ligado, recebe o Handshake e posteriormente recebe os pacotes e completa a transmissão.

Client e Server 4 = Descrevem 2 situações diferentes:

* Server 4 = Na primeira, a janela do Client é fechada durante a transmissão. Após 10 tentativas de reenviar a resposta de um dado pacote para o Client, o Server entra em Timeout e para a transmissão.

* Client 4 = Na segunda, a janela do Server é fechada durante a transmissão. Após 4 tentativas de enviar a resposta de um dado pacote para o Server, o Client entra em Timeout e para a transmissão.

Vale notar que a situação do 4 é realizada em duas instâncias diferentes, já que o log da janela fechada é descartada.
