try =>:
    var x => 10 / 0;
    ec.print(x);
<==> catch error =>:
    ec.print("Capturado: {error}");
<==>