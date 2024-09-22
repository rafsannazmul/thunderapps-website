<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = htmlspecialchars($_POST['name']);
    $email = htmlspecialchars($_POST['email']);
    $message = htmlspecialchars($_POST['message']);

    $to = "support@thunderapps.xyz";
    $subject = "New Contact Us Message";
    $headers = "From: " . $email . "\r\n" .
               "Reply-To: " . $email . "\r\n" .
               "Content-Type: text/html; charset=UTF-8";

    $email_body = "
    <h2>New Message from Contact Form</h2>
    <p><strong>Name:</strong> $name</p>
    <p><strong>Email:</strong> $email</p>
    <p><strong>Message:</strong></p>
    <p>$message</p>
    ";

    // Send the email
    if (mail($to, $subject, $email_body, $headers)) {
        echo "Message sent successfully!";
    } else {
        echo "Failed to send the message.";
    }
}
?>
