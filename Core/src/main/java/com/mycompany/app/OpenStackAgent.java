package com.mycompany.app;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;

import org.openstack4j.api.Builders;
import org.openstack4j.api.OSClient.OSClientV3;
import org.openstack4j.model.common.ActionResponse;
import org.openstack4j.model.common.Identifier;
import org.openstack4j.model.compute.FloatingIP;
import org.openstack4j.model.compute.Server;
import org.openstack4j.model.compute.ServerCreate;
import org.openstack4j.model.network.NetFloatingIP;
import org.openstack4j.openstack.OSFactory;

public class OpenStackAgent extends Thread{

	public String metodo = "";
	public String DATA_IP = "";
	
	public OpenStackAgent(String metodo, String DATA_IP){
		this.metodo = metodo;
		this.DATA_IP = DATA_IP;
	}
	
	
	public OpenStackAgent(){}
	
	public ServerCreate createInstance(String serverName, String flavorId, String keyParsName, String imageId){

		//lock para ser usado numa rotina de loop em tentativas de ciar servidor
		boolean lock = false;
		
		//numero de tentativas de criar um servidor
		int attempts = 1;

		//Objeto instancia a ser criado
		ServerCreate instance = null;

		//O loop � interrompido ap�s ocorrer cinco tentativas;
		while((lock!=true) && (attempts < 5)){
			try{
				System.out.println("\nTrying create a server... Try number: "+attempts);
				instance = Builders.server().name(serverName).flavor(flavorId).keypairName(keyParsName).image(imageId).build();
				Thread.sleep(10000);
				lock = true;
				attempts = 5;
			}catch(Exception e){
				System.out.println("\nError while trying create a server..."+e.getMessage());
				attempts = attempts+1;
				e.printStackTrace();
			}
		}
		if(lock == true){
			return instance;
		}
		else{
			System.out.println("Could not create server after: "+attempts+" attempts");
			return null;
		}
	}
	public boolean startInstance(ServerCreate serverCreated){

		/*
		 * Procedimento para autentica��o no OpenStack para consumir recursos da Nuvem;
		 */
		OSClientV3 os = null;

		try{
			os = OSFactory.builderV3()
					.endpoint("http://200.19.151.205:35357/v3")
					.credentials("rodrigo.moreira@ufu.br", "rodrigo.moreira", Identifier.byName("default"))
					.authenticate();
			//System.out.println("Authenticated!");
		}catch(Exception e){
			System.out.println("Error while authenticating...");
			System.out.println(e.getMessage());
		}


		boolean lock = false;
		int attempts = 1;
		while((lock!=true) && (attempts < 5)){
			try{
				System.out.println("Trying to start a server... Try number: "+attempts);
				os.compute().servers().boot(serverCreated);
				Thread.sleep(10000);
				lock = true;
				attempts = 5;

			}catch(Exception e){
				attempts = attempts+1;
				System.out.println("\nError starting instance: "+e.getMessage());
			}
		}
		if(lock == true){
			return true;
		}
		else{
			System.out.println("Could not start Server: "+serverCreated.getName()+" after: "+attempts+" attempts...");
			return false;
		}
	}
	public void deleteInstance(String instanceID){
		OpenStack stack = new OpenStack();
		OSClientV3 os = null;

		try{
			os = OSFactory.builderV3()
					.endpoint("http://200.19.151.205:35357/v3")
					.credentials("rodrigo.moreira@ufu.br", "rodrigo.moreira", Identifier.byName("default"))
					.authenticate();
			//System.out.println("Authenticated!");
		}catch(Exception e){
			System.out.println("Error while authenticating... Delete Instance");
			System.out.println(e.getMessage());
		}
		if(os.compute().servers().delete(instanceID).isSuccess()){
			System.out.println("SIP Server has been completely removed");
		}
		else{
			System.out.println("Problem while deallocating cloud feature...");
		}
		
		
	}
	public boolean shutOffInstance(String instanceID){
		return true;
	}
	public boolean restartInstance(String instanceID){
		return true;
	}
	public boolean assingFloatIP(ServerCreate serverCreated){
		
		OpenStack stack = new OpenStack();
		OSClientV3 os = null;

		try{
			os = OSFactory.builderV3()
					.endpoint("http://200.19.151.205:35357/v3")
					.credentials("rodrigo.moreira@ufu.br", "rodrigo.moreira", Identifier.byName("default"))
					.authenticate();
			//System.out.println("Authenticated!");
		}catch(Exception e){
			System.out.println("Error while authenticating... Assing Float IP");
			System.out.println(e.getMessage());
		}
		
		int tentativas = 1;
		String idIpFlutuante = stack.getAllocateFloatIpID().toString();
		do{
			if(idIpFlutuante.equals("NotFound")){
				if(stack.allocateFloatIP()){
					idIpFlutuante = stack.getAllocateFloatIpID().toString();
					NetFloatingIP netFloatingIP = os.networking().floatingip().get(idIpFlutuante);
					Server server = os.compute().servers().get(stack.getServerID(serverCreated.getName()));
					os.compute().floatingIps().addFloatingIP(server, netFloatingIP.getFloatingIpAddress());
					return true;
				}
				else{
					System.out.println("Error to Alocate Floating IP - Trying: "+tentativas);
				}
			}
			else{
				NetFloatingIP netFloatingIP = os.networking().floatingip().get(idIpFlutuante);
				Server server = os.compute().servers().get(stack.getServerID(serverCreated.getName()));
				os.compute().floatingIps().addFloatingIP(server, netFloatingIP.getFloatingIpAddress());
				return true;
			}
			tentativas = tentativas + 1;
		}while(tentativas <=5);
		return false;
	}
	
	public void run(){
		
		OpenStack stack = new OpenStack();
		stack.computeSurvey();

		
		/*
		 * Necessário verificar qual caminho a thread OpenStackAgent irá tomar, se e de exclusao de instancia ou criacao de instancia;
		 */
		if(this.metodo.equals("DELETE")){
			for(int i = 0; i < stack.getSipServersList().size(); i++){
				if(stack.getSipServersList().get(i).getDATA_IP_ADRESS().equals(this.DATA_IP)){
					SIPLoadBalancer lbConfig = new SIPLoadBalancer();
					/*
					 * Deleto aqui um servidor de destino de balanceamento
					 */
					if(SIPLoadBalancer.delete(stack.getSipServersList().get(i).getINSTANCE_NAME())){
						
						//Registro tempo Delecao Maquina
						this.registraTempo("Deletando VM");
						
						/*
						 * Aqui é reconfigurado a lista de prioridades do kamailio;
						 */
						lbConfig.prioritySetting("DELETE",stack.getSipServersList().get(i).getINSTANCE_NAME());
						
						
						/*
						 * Aqui é recarregado as configuraçoes de balanceamento do kamailio - 'kamctl dispatcher dump' - se for recarregado o VM poderá ser deletada;
						 */
						if(lbConfig.kamailioReloadConfigs()){
							/*
							 * Chamada do método para excluir a VM no OpenStack;
							 */
							this.deleteInstance(stack.getSipServersList().get(i).getINSTANCE_ID());
							/*
							 * Aqui devo retornar para que o bloco de criação de máquinas não seja iniciado
							 */
							
							/*
							 * Aqui é liberado para exclusão de mais máquinas se estiverem com Ociosidade demasiada;
							 */
							ComputeMonitor.RUNNING_DELETE = false;
							
							//Aqui e forcado a interrupcao da Thread que deletou a Instancia
							this.interrupt();
						}
					}
					
				}
			}
			return;
		}
		
		
		
		/*
		 * Procedimento para autentica��o no OpenStack para consumir recursos da
		 * Nuvem;
		 */
		OSClientV3 os = null;

		try {
			os = OSFactory.builderV3().endpoint("http://200.19.151.205:35357/v3").credentials("rodrigo.moreira@ufu.br", "rodrigo.moreira", Identifier.byName("default")).authenticate();
			// System.out.println("Authenticated!");
		} catch (Exception e) {
			System.out.println("Error while authenticating...");
			System.out.println(e.getMessage());
		}

		// Aqui e verificado se foi possivel alocar um IP flutuante - se for,
		// ocorrer� o prosseguimento de cria��o de uma Inst�ncia no OpenStack;

		int attempts = 1;

		
		//Aqui e registrado inicio da criacao de uma maquina
		this.registraTempo("Criando VM");
		
		ServerCreate serverCreated = createInstance("KSR" + (stack.getSipServersList().size() + 1),stack.getFlavorID("1.1"), "key_k-ims", stack.getImageID("MatrizKamailio"));
		System.out.println("The server was created: " + serverCreated.getName());
		if (startInstance(serverCreated)) {
			System.out.println("Service initialized!");
			if (!assingFloatIP(serverCreated)) {
				System.out.println("Error assigning Floating IP Address");
			}
			else{
				System.out.println("Floating IP successfully allocated...");
				SIPLoadBalancer lbConfig = new SIPLoadBalancer();
				String serverCONTROL_IP = "";  

				/*
				 * Aqui será necessário realizar um compute_survey de forma que já venha com IP de controle da nova máquina criada
				 * Bem como o nome da máquina para ser usado na description;
				 */
				stack.computeSurvey();
				for(int i = 0; i < stack.getSipServersList().size(); i++){
					if(stack.getSipServersList().get(i).getINSTANCE_NAME().equals(serverCreated.getName())){
						serverCONTROL_IP = stack.getSipServersList().get(i).getCONTROL_IP_ADRESS();
						lbConfig.insertLoadBalcerEntry(serverCONTROL_IP, lbConfig.prioritySetting("INSERT",serverCreated.getName()), serverCreated.getName());
						
						/*
						 * Colocar a Thread para aguardar que a nova instancia esteja 100% ociosa - segundo as estatisticas tempo gasto de 30 Segundos
						 */
						try{Thread.sleep(39000);}catch(Exception e){System.out.println("Erro ao compensar tempo de UpScalling das Instancias"+e.getMessage());}
						
						if(lbConfig.kamailioReloadConfigs()){
							System.out.println("Scalling up was concluded with success!");
							
							//Registra aqui o termino da criacao da maquina
							this.registraTempo("Concluida Criação VM");
							
						}
						else{
							System.out.println("Scalling UP Failure - Check Kamailio dispatcher from Orchestrator!");
						}
					}
				}
			}
		}
		
		/*
		 * Aqui é liberado para exclusão de mais máquinas se estiverem com Ociosidade demasiada;
		 */
		ComputeMonitor.RUNNING_SCHEDULING = false;
		
		//Forca interrupcao da Thread, pois ja finalizou a execucao;
		try{
			this.interrupt();
		}catch(Exception e){System.out.println("Erro ao interrponter Thread para criacao de uma VM"+e.getMessage());}
	}
	public void registraTempo(String msg){
		DateFormat dateFormat = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss");
		Date date = new Date();
		System.out.println(msg + " - "+dateFormat.format(date));
	}
}
