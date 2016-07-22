package com.dtf.client;

import android.app.IntentService;
import android.content.Intent;
import android.util.Log;


public class HelperService extends IntentService {

    private static final String ACTION_RESTART_SOCKET = "com.dtf.action.name.RESTART_SOCKET";

    private static final String TAG = "DtfHelperService";

    public HelperService() {
        super("HelperService");
    }

    @Override
    protected void onHandleIntent(Intent intent) {
        if (intent != null) {
            final String action = intent.getAction();

            if (ACTION_RESTART_SOCKET.equals(action)) {
                handleActionRestartSocket();
            }
        }
    }

    private void handleActionRestartSocket() {

        if (SocketService.isRunning) {

            // First stop the socket service.
            Log.d(TAG, "Stopping the socket service...");

            this.stopService(new Intent(this, SocketService.class));

        } else {
            Log.d(TAG, "Socket service is not running, skipping...");
        }

        // Give it 2 seconds to cool down
        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        // Now start it!
        Log.d(TAG, "Starting socket service!");
        this.startService(new Intent(this, SocketService.class));
    }
}
