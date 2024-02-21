<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = $_POST["name"];
    $email = $_POST["email"];
    $message = $_POST["message"];

    // Set up the recipient email address
    $to = "edgarmendonca96@gmail.com";

    // Set up the email subject
    $subject = "Message from your website";

    // Set up the email body
    $body = "Name: $name\n";
    $body .= "Email: $email\n";
    $body .= "Message:\n$message";

    // Send the email
    if (mail($to, $subject, $body)) {
        echo "Thank you for your message. We'll be in touch shortly!";
    } else {
        echo "Oops! Something went wrong. Please try again later.";
    }
}
?>
