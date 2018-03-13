using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ExampleProject
{
    /// <summary>
    /// Represents a device
    /// </summary>
    public class Device
    {
        /// <summary>
        /// Gets or sets the device's serial port
        /// </summary>
        /// <value>The name of the serial port</value>
        public string Port { get; set; }

        /// <summary>
        /// Creates an instance of the device.
        /// </summary>
        /// <remarks>Note that you must set the <see cref="Port"/> before attempting to <see cref="Open"/> the connection.</remarks>
        public Device()
        {

        }

        /// <summary>
        /// Creates an instance of the device.
        /// </summary>
        /// <param name="port">The serial port where the device is located.</param>
        public Device(string port)
        {
            Port = port;
        }

        /// <summary>
        /// Begins communication with the device on the selected port (<see cref="Port"/>).
        /// </summary>
        /// <returns><c>true</c> if the connection was done successfully, <c>false</c> otherwise.</returns>
        public Boolean Open()
        {
            return true;
        }

        /// <summary>
        /// Ends communication with the device
        /// </summary>
        public void Close()
        {
        }

        /// <summary>
        /// Restarts the device with the default configuration
        /// </summary>
        public void Restart()
        {

        }

        /// <summary>
        /// Restarts the device.
        /// </summary>
        /// <param name="flags">Configuration flags to start the device with.</param>
        public void Restart(int flags)
        {

        }


    }
}
