<?php
session_start();

$message = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Sanitize and validate inputs
    $name = filter_var($_POST["name"], FILTER_SANITIZE_STRING);
    $email = filter_var($_POST["email"], FILTER_SANITIZE_EMAIL);
    $subject = filter_var($_POST["subject"], FILTER_SANITIZE_STRING);
    $messageBody = filter_var($_POST["message"], FILTER_SANITIZE_STRING);

    // Validate email format
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $message = "Invalid email format";
        $_SESSION['message'] = $message;
        header("Location: index.html?formSubmitted=false");
        exit();
    }

    $to = "edgarmendonca96@gmail.com";
    $subject = "Contact Form Submission - $subject";

    $headers = "From: $email" . "\r\n" .
               "Reply-To: $email" . "\r\n" .
               "Content-type: text/html; charset=UTF-8";

    $mailBody = "
    <html>
    <body>
        <h2>Contact Form Submission</h2>
        <p><strong>Name:</strong> $name</p>
        <p><strong>Email:</strong> $email</p>
        <p><strong>Subject:</strong> $subject</p>
        <p><strong>Message:</strong> $messageBody</p>
    </body>
    </html>";

    if (mail($to, $subject, $mailBody, $headers)) {
        $message = "Message sent successfully!";
        $_SESSION['message'] = $message;
    } else {
        $message = "Failed to send message. Please try again later.";
        $_SESSION['message'] = $message;
    }
}

header("Location: contact.html?formSubmitted=" . (isset($_SESSION['message']) ? 'true' : 'false'));
exit();
