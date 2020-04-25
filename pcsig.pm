//create by Cleber Brito Santos em 29/05/2019

dtmc	//Modelo probabilistico utilizado - Discrete Time Markov Chain

formula validacao = mudancaDoTurnoDoLider=L;  
formula turnoDoLider = mudancaDoTurnoDoLider=i; 
formula dadosDaVisao = mudancaDoTurnoDoLider=1 ? 1:2;
//formula dadosDaVisaoe = mod(phase_token,2) = 0;

const double taxaDePerdaDeMensagens;	
const int tempoLimite= 1;		      
const int contadorVersao = 4; 
const int L = 3;		
const int i = 1;		
const int j = 2;		 
const int enviar = 0;	        
const int receber = 1;		
const int semInformacao = 0;		
const int contSync = 10;
//const int dadosDaVisao = 1;

global tarefa : [enviar..receber] init 0;	
global mudancaDoTurnoDoLider : [1..L] init 1;	
global x : [1..11] init 1; 
global verificaSyncBidirecional : bool init false;
global bidirecional : bool init false;  
global etapaManutencao : bool init false;
global variavelDeGiro : [0..1] init 0; 
global verificaBidirecional : bool init false;

module lider_i
       cronometro_i : [0..2] init 0;	
       visoesSincronizadas_i : bool init false;	

//VARIAVEIS UTILIZADAS PARA DEFINIR O QUE UM LIDER DE PELOTAO SABE DE SUA VISAO E DA VISAO DO OUTRO PELOTAO
       visao_i : [0..contadorVersao] init 0;	
       visoesConhecidas_i : [0..contadorVersao] init 0;	
       visoesRecebidas_i : [0..contadorVersao] init 0;
       visoesConhecidasRecebidas_i : [0..contadorVersao] init 0;

//TODAS AS VARIAVEIS SAO RESETADAS PARA REINICIO DA VERIFICACAO       
       [] turnoDoLider & tarefa=enviar & cronometro_i=tempoLimite & x > contSync & verificaSyncBidirecional=false -> (mudancaDoTurnoDoLider'=mudancaDoTurnoDoLider+1) & 
       (visoesRecebidas_i'=semInformacao) & (visao_i'=semInformacao) & (visoesConhecidas_i'=semInformacao)  & (visoesConhecidasRecebidas_i'=semInformacao) 
       & (visoesSincronizadas_i'=false) & (cronometro_i'=semInformacao) & (bidirecional'=false);

//TAREFA 1 - RESPONSAVEL PELO ENVIO PERIODICO DE MENSAGENS
       [] turnoDoLider & tarefa=enviar -> 
       (visao_i'=dadosDaVisao) & (visoesConhecidas_i'=visoesRecebidas_i) & (mudancaDoTurnoDoLider'=mudancaDoTurnoDoLider+1); 

//TAREFA 2 - RESPONSAVEL PELO RECEBIMENTO DE MENSAGENS
       [] turnoDoLider & tarefa=receber  & cronometro_i<tempoLimite -> 
       (1-taxaDePerdaDeMensagens) : (cronometro_i'=cronometro_i+1) & (mudancaDoTurnoDoLider'=mudancaDoTurnoDoLider+1) & (visoesRecebidas_i' = visao_j)
       & (visoesConhecidasRecebidas_i'=visoesConhecidas_j)
       + 
       (taxaDePerdaDeMensagens) : (cronometro_i'=cronometro_i+1) & (mudancaDoTurnoDoLider'=mudancaDoTurnoDoLider+1);               
       [] turnoDoLider & tarefa=receber & cronometro_i=tempoLimite & etapaManutencao=false -> //
       (1-taxaDePerdaDeMensagens) : (etapaManutencao'=true) & (visoesRecebidas_i' = visao_j) & (visoesConhecidasRecebidas_i'=visoesConhecidas_j)
       + 
       (taxaDePerdaDeMensagens) : (etapaManutencao'=true);

       //ETAPA DE MANUTENCAO
       [] turnoDoLider & etapaManutencao=true & visoesConhecidasRecebidas_i=visao_i -> 
       (visoesSincronizadas_i' = true) & (etapaManutencao'=false) & (mudancaDoTurnoDoLider'=mudancaDoTurnoDoLider+1) & (verificaBidirecional'=true) 
        & (cronometro_i'=0);        
       [] turnoDoLider & etapaManutencao=true & visoesConhecidasRecebidas_i!=visao_i -> 
       (visoesSincronizadas_i' = false) & (etapaManutencao'=false) & (mudancaDoTurnoDoLider'=mudancaDoTurnoDoLider+1) & (verificaBidirecional'=true) 
        & (cronometro_i'=0);
endmodule

module mudancaDeAcao       
//UTILIZADO PARA A REALIZACAO DE MUDANCA DE ESTADOS       
       [] validacao & tarefa = enviar & variavelDeGiro=0 & verificaSyncBidirecional=false -> (tarefa' = receber) & (mudancaDoTurnoDoLider'=i);
       [] validacao & tarefa = enviar & variavelDeGiro=1  & x <= contSync -> (verificaSyncBidirecional'=false) & (mudancaDoTurnoDoLider'=i) 
       & (variavelDeGiro'=0); 
       [] validacao & tarefa = enviar  & x > contSync -> (mudancaDoTurnoDoLider'=i) & (x'=1) ; 
       [] validacao & tarefa = receber & verificaSyncBidirecional=false & verificaBidirecional=false & x<=10 -> (tarefa'=enviar) & (mudancaDoTurnoDoLider'=i); 
       [] validacao & tarefa = receber & verificaSyncBidirecional=false & verificaBidirecional=false & x>10 -> (tarefa'=enviar) & (mudancaDoTurnoDoLider'=i) & (x'=1); 
       
//UTILIZADO PARA CONTABILIZACAO DAS RECOMPENSAS
//-----------------------------------------------------------------------------------------------------------------------------------------//
       [] validacao & visoesSincronizadas_i=true & visoesSincronizadas_j=true & verificaBidirecional=true -> 
       (bidirecional'=true)  & (verificaBidirecional'=false) & (verificaSyncBidirecional'=true); 
       [] bidirecional=true & verificaBidirecional=false & x <= contSync & verificaSyncBidirecional=true 
       -> (tarefa'=enviar) & (mudancaDoTurnoDoLider'=i) & (x'=x+1) & (bidirecional'=false) & (verificaSyncBidirecional'=false); 
       []validacao & (visoesSincronizadas_i!=true|visoesSincronizadas_j!=true) & verificaBidirecional=true -> 
       (bidirecional'=false)  & (verificaBidirecional'=false) & (verificaSyncBidirecional'=true);        
       [] bidirecional=false  & verificaBidirecional=false & x <= contSync & verificaSyncBidirecional=true 
       -> (tarefa'=enviar) & (mudancaDoTurnoDoLider'=i) & (x'=x+1) & (verificaSyncBidirecional'=false); 
//-----------------------------------------------------------------------------------------------------------------------------------------//
endmodule

module lider_j=lider_i
       [i=j, cronometro_i=cronometro_j, visoesRecebidas_i=visoesRecebidas_j,visoesRecebidas_j=visoesRecebidas_i, visao_j=visao_i,visao_i=visao_j, 
        visoesConhecidas_i=visoesConhecidas_j, 
        visoesConhecidas_j=visoesConhecidas_i, visoesSincronizadas_j=visoesSincronizadas_i, visoesSincronizadas_i=visoesSincronizadas_j, 
       visoesConhecidasRecebidas_i=visoesConhecidasRecebidas_j] 
endmodule

rewards  bidirecional=true : 1; endrewards
