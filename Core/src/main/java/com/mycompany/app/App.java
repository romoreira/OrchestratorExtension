package com.mycompany.app;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Hello world!
 *
 */

public class App {

	//Para registrar o currentTime em cenarios de experiemnto
	public void upTimeExperiment() {
		OpenStackAgent deleteComputeThread = new OpenStackAgent("", "");

		DateFormat dateFormat = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss");
		Date date = new Date();
		System.out.println(dateFormat.format(date));
		OnosControllerAgent oca = new OnosControllerAgent();
		//deleteComputeThread.run();
	}

	public static void main(String[] args) {

		//Inicio da Thread para monitoramento dos recursos de Compute;
		ComputeMonitor compute = new ComputeMonitor();
		Thread computeThread = new Thread(compute);
		//computeThread.start();

		//Inicio da Thread para monitoramento dos recursos de Network;
		Network network = new Network();
		network.init();
	}
}






























/*
 * // networkAgent.setHostToHostInent(fibre.getHostList().get(0).getID_HOST(),
 * fibre.getHostList().get(1).getID_HOST()); //
 * networkAgent.removeHostToHostIntent("org.onosproject.cli", "0x0");
 * 
 * // OpenStack computeAgent = new OpenStack(); // computeAgent.getTste(); // //
 * networkAgent.removeFlows(); //
 * networkAgent.removeDevice("of:0000000000000903"); //
 * networkAgent.removeDevice("of:0000000000000901"); //
 * networkAgent.removeDevice("of:0000000000000902");
 */