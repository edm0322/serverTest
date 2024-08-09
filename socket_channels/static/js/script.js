document.addEventListener('DOMContentLoaded', function() {
    const socket = new WebSocket('ws://' + window.location.host + '/ws/command/');
    const clientSelect = document.getElementById('client-select');
    const clientList = document.getElementById('client-list');
    const resultContainer = document.getElementById('result-container');
	const clientCountElement = document.getElementById('client-count');

    socket.onopen = function(e) {
        console.log("WebSocket connection established");
    };

    socket.onmessage = function(event) {
        console.log("Message received from server:", event.data);
        const data = JSON.parse(event.data);
        if (data.type === 'command_result') {
            displayCommandResult(data);
        } else if (data.type === 'client_list_update') {
            updateClientList(data.clients);
			updateClientCount(data.client_count);
        }
    };

    socket.onerror = function(error) {
        console.error("WebSocket error:", error);
    };

    document.getElementById('send-command').addEventListener('click', function() {
        const clientId = clientSelect.value;
        const command = document.getElementById('command-input').value;
        console.log("Sending command:", command, "to client:", clientId);
        socket.send(JSON.stringify({
            type: 'command_request',
            target_client: clientId,
            command: command
        }));
    });

    function updateClientList(clients) {
        clientSelect.innerHTML = '<option value="">Select a client</option>';
        clientSelect.innerHTML += '<option value="all">All Clients (except localhost) </option>';
        clientList.innerHTML = '<h3>Connected Clients:</h3>';
        clients.forEach(client => {
			if(client !== '127.0.0.1' && client !== 'localhost') {
	            const option = document.createElement('option');
    	        option.value = client;
        	    option.textContent = client;
            	clientSelect.appendChild(option);

	            const div = document.createElement('div');
    	        div.textContent = client;
        	    clientList.appendChild(div);
			}
        });
    }

	function updateClientCount(count){
			clientCountElement.textContent = `Connected Client Count: ${count}`;
	}

    function displayCommandResult(data) {
        const resultDiv = document.createElement('div');
        resultDiv.innerHTML = `<strong>Client ${data.client_id}:</strong> ${data.command}<br>Result: ${data.result}`;
        resultContainer.appendChild(resultDiv);
        resultContainer.scrollTop = resultContainer.scrollHeight;
    }
});
