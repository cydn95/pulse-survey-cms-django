#!/bin/bash

# for now we are just checking that we get back a page from the server
echo "################################################################"
echo "Validating Server"
echo "################################################################"
curl -L http://localhost:8000/admin

echo "################################################################"
echo "Validated Server"
echo "################################################################"
