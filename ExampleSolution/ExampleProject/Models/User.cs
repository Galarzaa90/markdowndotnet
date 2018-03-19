using System;
namespace ExampleProject.Models
{
    /// <summary>
    /// Represents a User
    /// </summary>
    public class User
    {
        public string Name { get; set; }
        public string LastName { get; set; }
        public int Age { get; set; }
        public Gender Gender { get; set; }

        public User()
        {

        }
    }

    /// <summary>
    /// Representes a user's gender.
    /// </summary>
    public enum Gender{
        /// <summary>
        /// Unspecified.
        /// </summary>
        UNSPECIFIED,
        /// <summary>
        /// Male.
        /// </summary>
        MALE, 
        /// <summary>
        /// Female.
        /// </summary>
        FEMALE
    }
}
