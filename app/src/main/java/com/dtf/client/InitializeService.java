/* Android Device Testing Framework ("dtf")
 * Copyright 2013-2014 Jake Valletta (@jake_valletta)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
package com.dtf.client;

import android.app.IntentService;
import android.content.Intent;
import android.content.res.AssetManager;
import android.util.Log;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

public class InitializeService extends IntentService {

	private final String TAG = "DtfInitializeService";

    public InitializeService() {
        super("InitializeService");
    }

    @Override
    protected void onHandleIntent(Intent intent) {

        Process p = null;
        try {
            p = Runtime.getRuntime().exec("chmod 777 /data/data/com.dtf.client/files");
            p.waitFor();
        } catch (InterruptedException e) {
            Log.e(TAG, "Unable to open permissions on files directory!");
        }
        catch (IOException e) {
            Log.e(TAG, "Unable to open permissions on files directory!");
        }

        Log.d(TAG, "Copying assets...");
        int resp = copyAssets();
        Log.d(TAG, "Copy completed: " + resp);

    }

    private int copyAssets() {
    	
        AssetManager assetManager = getAssets();
        String[] files = null;
        
        try {
            files = assetManager.list("");
        } catch (IOException e) {
            Log.e("tag", "Failed to get asset file list.", e);
            return -1;
        }
        
        for(String filename : files) {
        	if (filename.equals("busybox")) {
        		        		
                InputStream in = null;
                OutputStream out = null;
                
                try {
                  in = assetManager.open(filename);
                  File outFile = new File(this.getFilesDir()+"/", filename);

                  out = new FileOutputStream(outFile);
                  copyFile(in, out);
                  in.close();
                  in = null;
                  out.flush();
                  out.close();
                  out = null;
                  
                  // Make it world executable.
                  outFile.setExecutable(true, false);
 
                } catch(IOException e) {
                    Log.e("tag", "Failed to copy asset file: " + filename, e);
                    return -2;
                }             		
        	}
        }
        return 0; 
    }
    
    private void copyFile(InputStream in, OutputStream out) throws IOException {
        byte[] buffer = new byte[1024];
        int read;
        while((read = in.read(buffer)) != -1){
          out.write(buffer, 0, read);
        }
    }	
}