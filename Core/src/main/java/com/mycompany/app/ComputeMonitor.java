package com.mycompany.app;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.net.BindException;
import java.net.ConnectException;
import java.net.ServerSocket;
import java.net.Socket;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.LinkedList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.Date;

//Essa classe ComputeMonitor dever� abrir um Socket e ouvir requisi��es POST vinda dos SIP servers;
public class ComputeMonitor extends OpenStack implements Runnable{

	public static boolean RUNNING_SCHEDULING = false;
	public static boolean RUNNING_DELETE = false;
	public String fileName = "";
	
	
	public String getFileName() {
		return fileName;
	}

	public void setFileName(String fileName) {
		this.fileName = fileName;
	}
	/*
	 * Aqui � definido o Threshold de ociosidade de CPU, menor que esse valor dever� ser disparado algum evento;
	 */
	public final Double CPU_THRESHOLD_OL = 10.0;//Threshold para alta utilização - 90% de utilização
	public final Double CPU_THRESHOLD_LL = 98.0;//Threshold para baixa utilização - 2% de utilização

	public OpenStack computeServices = new OpenStack();
	JSONProcessor json = new JSONProcessor();

	public boolean checkLowLoad(String DATA_IP){
		/*
		 * Aqui e verificado se o consudmo de historico de CPU esta dentro dos parametros de Threshold -  se estiver, sera retornado um valor verdade;
		 */
		for(int i = 0; i < computeServices.getSipServersList().size(); i++){

			if(DATA_IP.equals(computeServices.getSipServersList().get(i).getDATA_IP_ADRESS().toString())){
				System.out.println("\nHistorico de CPU Ociosa: "+computeServices.getSipServersList().get(i).getCPU_HISTORY().toString());
				System.out.println("IP da Maquina: "+computeServices.getSipServersList().get(i).getDATA_IP_ADRESS());
				/*
				 * Aqui é verificado se a média de consumo de CPU ociosa e maior que o Threshold -quando for significa que máquina está com baixa utilizaão e poderá ser excluída;
				 * IMPORTANTE: deverá ser verificado se a media de consumo é diferente de -1 será igual a -1 quando não tiver histórico, ou seja, menos que três amostras;
				 */
				if((averageCPU_USAGE(this.computeServices.getSipServersList().get(i).getCPU_HISTORY()) > this.CPU_THRESHOLD_LL) && (averageCPU_USAGE(this.computeServices.getSipServersList().get(i).getCPU_HISTORY()) != -1.0)){
					System.out.println("Low utilization!");
					return true;
				}
			}
		}
		return false;
	}
	
	/*
	 * Aqui devera ser retornoado um valor verdade se a Instancia esta em OverLoad;
	 */
	public boolean checkOverLoad(String DATA_IP){

		/*
		 * Aqui e verificado se o consumo historico de CPU esta dentro dos parametros de Threshold - se estiver, sera retornado um valor verdade;
		 */
		for(int i = 0; i < computeServices.getSipServersList().size(); i++){

			if(DATA_IP.equals(computeServices.getSipServersList().get(i).getDATA_IP_ADRESS().toString())){
				//System.out.println("Historico de CPU: "+computeServices.getSipServersList().get(i).getCPU_HISTORY().toString());
				//System.out.println("IP da Maquina: "+computeServices.getSipServersList().get(i).getDATA_IP_ADRESS());
				
				/*
				 * Aqui é verificado se a média de CPU ociosa está abaixo do aceitável - não estará quando estiver com alta utilização
				 * IMPORTANTE: deverá ser verificado também e o histórico não é igual a -1.0 - será quando não tiver valores de CPU_UTIL suficientes para calcular uma media de utilizaão
				 */
				
				if((averageCPU_USAGE(this.computeServices.getSipServersList().get(i).getCPU_HISTORY()) < this.CPU_THRESHOLD_OL) && (averageCPU_USAGE(this.computeServices.getSipServersList().get(i).getCPU_HISTORY()) != -1.0)){
					System.out.println("!!!High utilization!!!");

					/*
					 * Uma vez que o Host foi acometido com consumo alto de CPU e resetado seu historico;
					 */
					LinkedList<Double> resetCpuHistory = new LinkedList<Double>();
					resetCpuHistory.add(100.0);
					resetCpuHistory.add(100.0);
					resetCpuHistory.add(100.0);
					computeServices.getSipServersList().get(i).setCPU_HISTORY(resetCpuHistory);

					/*
					 * Aqui e retornado o valor verdade true pois devera ser criado um novo Host;
					 */
					return true;
				}
			}
		}
		return false;
	}

	public void updateCPU_USAGE(String DATA_IP_SERVER, String cpu_util){
		Double value = 0.0;
		//System.out.println("IP do host que sera atualizado o uso de CPU: "+DATA_IP_SERVER);
		//System.out.println("CPU UTIL: "+cpu_util);
		this.writeCPU_usage(DATA_IP_SERVER+";"+cpu_util+";"+this.getTimeCPU_UTIL());
		value = Double.parseDouble(cpu_util);
		if(value > 100){
			return;
		}
		for(int i = 0; i < this.computeServices.getSipServersList().size(); i++){
			if(this.computeServices.getSipServersList().get(i).getDATA_IP_ADRESS().equals(DATA_IP_SERVER)){
				if(this.computeServices.getSipServersList().get(i).getCPU_HISTORY().size() < 3){
					this.computeServices.getSipServersList().get(i).getCPU_HISTORY().addLast(value);
				}
				else{
					this.computeServices.getSipServersList().get(i).getCPU_HISTORY().addLast(value);
					this.computeServices.getSipServersList().get(i).getCPU_HISTORY().removeFirst();
				}
			}
		}
	}
	
	public String getTimeCPU_UTIL(){
		DateFormat dateFormat = new SimpleDateFormat("yyyy/MM/dd HH:mm:ss");
		Date date = new Date();
		return dateFormat.format(date).toString();
	}
	
	public void createFile(){
		/*
		 * Para o nome do arquivo de saída vir com a data de criação;
		 */		
		DateFormat dateFormat = new SimpleDateFormat("yyyyMMddHHmmSS");
		Date date = new Date();
		dateFormat.format(date);
		String fileName = dateFormat.format(date)+"cpu_health.txt";
		File arquivo = new File(fileName);
		this.setFileName(fileName);
	}
	
	public void writeCPU_usage(String texto){
		try{
			BufferedWriter arquivo = new BufferedWriter(new FileWriter(this.getFileName(),true));
			arquivo.newLine();
			arquivo.write(texto);
			arquivo.flush();
			arquivo.close();
		}catch(Exception e){
			System.out.println("Error to write CPU Healt in to File"+e.getMessage());
		}
	}
	
	/*
	 * Aqui dever� ser retornado uma m�dia de tres amostras de consumo de CPU,
	 */
	public Double averageCPU_USAGE(LinkedList<Double> samples){

		//System.out.println("Chegou apra calcular a media");

		/*
		 * Aqui e verificado se existem pelomenos 3 amostras para calcular a media - caso nao haja, sera retornado 100 (ou seja, CPU 100 ociosa)
		 */
		if(samples.size() < 3){
			return -1.0;
		}

		Double avg = 0.0;

		/*
		 * Aqui � percorrido a amostra de consumo de CPU de um determinado host, ser� retornado a m�dira aritim�tica;
		 */
		for(int i = 0; i < 3; i++){
			avg = avg + samples.get(i);
		}
		if(samples.size() == 3){
			//System.out.println("Media de utilizacao: "+(avg/3));
			return (avg/3);
		}
		return -1.0;
	}

	public void computeCollector() {

		try {

			//Crio o servi�o de monitoramento, ele ficar� ouvindo na porta 8181
			ServerSocket welcomeSocket = new ServerSocket(7070);

			while (true) {

				//Metodo e iniciado quando recebe qualquer mensagem na porta que o Socket foi criado
				Socket socket = welcomeSocket.accept();

				//Definicao de variaveis para leitura da mensagem Bufferizada na rede, tambem para Escrita de mensagem de sucesso
				BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
				BufferedWriter out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));


				//Aqui e onde sera lido o cabecalho das mensagens recebidas
				String line;
				line = in.readLine();
				StringBuilder raw = new StringBuilder();
				raw.append("" + line);
				boolean isPost = line.startsWith("POST");
				int contentLength = 0;
				while (!(line = in.readLine()).equals("")) {
					raw.append('\n' + line);

					//Se o metodo for POST as linhas abaixo farao a conta de qual tamanho da mensagem JSON
					if (isPost) {
						final String contentHeader = "Content-Length: ";
						if (line.startsWith(contentHeader)) {
							contentLength = Integer.parseInt(line
									.substring(contentHeader.length()));
						}
					}

				}

				//Onde e computado o tamanho da mensagem JSON
				StringBuilder body = new StringBuilder();
				if (isPost) {
					int c = 0;
					for (int i = 0; i < contentLength; i++) {
						c = in.read();
						body.append((char) c);
					}
				}


				//Nesse trecho e extraido somente a mensagem JSON da cadeia de caracteres recebidas, o que inclui destination e outros
				raw.append(body.toString());
				String JSON = "";
				JSON = body.toString();

				//TEMPORARIO: Exibir a mensagem JSON
				//System.out.println(JSON);
				String cpuMeters = JSON.substring(JSON.indexOf("Content-Length: ") + 1, JSON.length());
				

				/*
				 * Aqui sera atualizado o consumo de CPU da maquina que enviou seu report;
				 */
				this.updateCPU_USAGE(this.json.getCpuIdleIP(cpuMeters),this.json.getCpuIdleValue(cpuMeters).toString());

				/*
				 * Aqui sera computado se o consumo de CPU esta nas margens permitidas, ou seja, abaixo do Threshold predefinido;
				 */
				if(this.checkOverLoad(this.json.getCpuIdleIP(cpuMeters))){
					System.out.println("Need to create a new server!!!");
					OpenStackAgent computeThread = new OpenStackAgent();
					
					/*
					 * Após ter acriado uma nova máquina é necessário fazer um compute_survey - para que a métrica recebida possa ser armazenada corretamente
					 */
					computeServices.computeSurvey();
					
					if(this.RUNNING_SCHEDULING == false){
						this.RUNNING_SCHEDULING = true;
						computeThread.start();
						
						/*
						 * Após ter acriado uma nova máquina é necessário fazer um compute_survey - para que a métrica recebida possa ser armazenada corretamente
						 */
						computeServices.computeSurvey();
					}
					else{
						System.out.println("\nCreating a new SIP-Sever is already in progress...");
					}
				}
				/*
				 * Se não estiver com alta utilização é verificado se a CPU está OCIOSA, se estiver, ela poderá ser destruída
				 */
				else{
					if(this.checkLowLoad(this.json.getCpuIdleIP(cpuMeters)) && (computeServices.getSipServersList().size() > 1)){
						OpenStackAgent deleteComputeThread = new OpenStackAgent("DELETE", this.json.getCpuIdleIP(cpuMeters));
						
						
						/*
						 * Após ter acriado uma nova máquina é necessário fazer um compute_survey - para que a métrica recebida possa ser armazenada corretamente
						 */
						computeServices.computeSurvey();
						
						/*
						 * Aqui é verificado se existe uma rotina de exclusão em andamento, se não tiver, ele entrará e travará a execução;
						 */
						if(this.RUNNING_DELETE == false){
							this.RUNNING_DELETE = true;
							deleteComputeThread.start();
							
							/*
							 * Após ter acriado uma nova máquina é necessário fazer um compute_survey - para que a métrica recebida possa ser armazenada corretamente
							 */
							computeServices.computeSurvey();
							this.RUNNING_DELETE = false;
						}
						else{
							System.out.println("\nAnother delete SIP-Serer is already in progress...");
						}
						
					}
				}

				//Aqui � enviado uma mensagem 'OK' informando que foi recebido o informativo de utiliza��o de CPU
				out.write("HTTP/1.1 200 OK\r\n");
				out.write("Content-Type: text/html\r\n");
				out.write("\r\n");
				out.write(new Date().toString());
				if (isPost) {
					out.write("<br><u>" + body.toString() + "</u>");
				} else {
					out.write("<form method='POST'>");
					out.write("<input name='name' type='text'/>");
					out.write("<input type='submit'/>");
				}
				out.write("</form>");

				//Para cada mensagem recebia � aberta e encarrada uma Conx�o, o trecho de c�dio abaixo encerra a Conex�o com o QoS-Awere
				out.flush();
				out.close();
				socket.close();


			}
		}
		catch(BindException e){
			System.out.println("Ja existe um SocketAberto\n"+e.getMessage());
		}
		catch (ConnectException e) {
			System.out.println("Erro ao Abrir o Socket\n" + e.getMessage());
		}
		catch(StringIndexOutOfBoundsException e){
			System.out.println("Ocorreu um erro ao corttar String para extrair o JSON\n"+e.getMessage());
		}
		catch (Exception e) {
			System.out.println("Erro Geral\n"+e.getMessage());
			e.printStackTrace();
			StringWriter sw = new StringWriter();
			e.printStackTrace(new PrintWriter(sw));
		}
	}
	public void run(){
		System.out.println("Monitoring Compute...");

		/*
		String metricaTemp = "{\"metrics\": [{\"type\": \"IntCounter\", \"name\": \"192.168.100.80|CpuUsage:user\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|CpuUsage:nice\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|CpuUsage:system\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|CpuUsage:idle\", \"value\": \"100\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|CpuUsage:iowait\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|CpuUsage:irq\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|CpuUsage:softirq\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|Load:load1\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|Load:load5\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|Load:load15\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:MemTotal\", \"value\": \"2058448\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:MemFree\", \"value\": \"1780764\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:MemAvailable\", \"value\": \"1809120\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Buffers\", \"value\": \"20584\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Cached\", \"value\": \"123660\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:SwapCached\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Active\", \"value\": \"174032\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Inactive\", \"value\": \"52172\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Active(anon)\", \"value\": \"82140\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Inactive(anon)\", \"value\": \"13548\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Active(file)\", \"value\": \"91892\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Inactive(file)\", \"value\": \"38624\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Unevictable\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Mlocked\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:SwapTotal\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:SwapFree\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Dirty\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Writeback\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:AnonPages\", \"value\": \"82008\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Mapped\", \"value\": \"37556\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Shmem\", \"value\": \"13732\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Slab\", \"value\": \"31280\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:SReclaimable\", \"value\": \"20924\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:SUnreclaim\", \"value\": \"10356\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:KernelStack\", \"value\": \"1952\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:PageTables\", \"value\": \"7732\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:NFS_Unstable\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Bounce\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:WritebackTmp\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:CommitLimit\", \"value\": \"1029224\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Committed_AS\", \"value\": \"839864\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:VmallocTotal\", \"value\": \"34359738367\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:VmallocUsed\", \"value\": \"3776\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:VmallocChunk\", \"value\": \"34359732503\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:HardwareCorrupted\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:AnonHugePages\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:HugePages_Total\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:HugePages_Free\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:HugePages_Rsvd\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:HugePages_Surp\", \"value\": \"0\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:Hugepagesize\", \"value\": \"2048\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:DirectMap4k\", \"value\": \"46976\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:DirectMap2M\", \"value\": \"2050048\"}, {\"type\": \"IntCounter\", \"name\": \"192.168.100.80|MemInfoKB:DirectMap1G\", \"value\": \"0\"}]}";
		JSONProcessor json = new JSONProcessor();
		System.out.println("Dentro do compute monitor - CPU: "+json.getCpuIdleValue(metricaTemp));
		System.out.println("Dentro do compute monitor - HOST: "+json.getCpuIdleIP(metricaTemp));
		 */

		this.createFile();
		this.writeCPU_usage("instance_ip;cpu_idle;time");
		this.computeServices.computeSurvey();
		this.computeCollector();
	}
}
