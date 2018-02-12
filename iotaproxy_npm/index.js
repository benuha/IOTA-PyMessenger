
/**
 * Simple proxy server for IOTA.
 * Relays commands to the IOTA Tangle, but intercepts attachToTangle commands and performs PoW locally.
 *
 * This proxy server useful for when you want to perform transfers with iota.lib.js in Node but do not
 * have access to a full node that grants you access to the necessary attachToTangle commands.
 */

var iotaProxy = require('./lib/iotaproxy.js');

iotaProxy.start(
  {
    host: 'http://node02.iotatoken.nl', // PUBLIC IOTA NODE, used to relay traffic to tangle. Other node: 'https://potato.iotasalad.org', but not yet support for https
    port: 14265,						// Port of PUBLIC NODE
    localPort: 14265,					// Listening on http://localhost for light node to send request to the proxy
    overrideAttachToTangle: true,		// Do the POW on proxy before replay to tangle because public node doesnot support for POW
    timeout: 15							// Time out in minutes
  }
);
