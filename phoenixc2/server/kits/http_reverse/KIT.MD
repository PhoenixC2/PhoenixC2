# Reverse-HTTP Kit

## Description

This kit allows you to create a reverse-HTTP stager that will connect back to the C2 server. This kit is useful for situations where you have a compromised host that you can't directly access, but you can access a web server on the same network. This kit will create a reverse-HTTP stager that will connect back to the C2 server and then use the C2 server to connect back to the compromised host.

## Process

1. Create a new listener using the `http_reverse`

2. Create a new stager using the listener you created in step 1

3. Download the code from the stager you created in step 2

4. Run the code on the compromised host

5. The stager will connect back to the C2 server




