using ExampleProject.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ExampleProject.Models
{
    /// <summary>
    /// Delegate for the <see cref="ApiClient.OnMessageReceived"/> event.
    /// </summary>
    /// <param name="message">The message received</param>
    public delegate void OnMessageHandler(Message message);
}
