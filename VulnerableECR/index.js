const express = require("express");
const app = express();

app.get("/", (req, res) => {
  res.send("This is my express app");
});

app.get("/me", (req, res) => {
  res.send("Hi I am Betsy!");
});

app.listen(5010, () => {
  console.log("listening");
});;
