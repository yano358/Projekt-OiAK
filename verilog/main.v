module PreProcessingNode(
	input A,
	input B,
	output G,
	output H,
	output P
);

	assign G = A & B;
	assign P = A | B;
	assign H = ~G & P;

endmodule

module PreProcessingNodeExtended(
	input A,
	input B,
	input K,
	input Bprim_in,
	output G,
	output H,
	output P,
	output Gprim,
	output Hprim,
	output Pprim,
	output Bprim_out
);

	wire Aprim_wire, Gprim_wire, Pprim_wire, Hprim_wire;

	PreProcessingNode first_node(
		.A(A),
		.B(B),
		.G(G),
		.H(H),
		.P(P)
	);
	
	assign Aprim = (K == 1'b1) ? ~H : H;

	PreProcessingNode second_node(
		.A(Aprim),
		.B(Bprim_in),
		.G(Gprim),
		.H(Hprim),
		.P(Pprim)
	);

	assign Bprim_out = (K == 1'b1) ? P : G;
endmodule

module ParallelPrefixNode(
	input G,
	input P,
	input Gprev,
	input Pprev,
	output Gout,
	output Pout
);
	assign Pout = P & Pprev;
	assign Gout = G | (Gprev & P);
endmodule

module ParallelPrefixNodeExtended(
	input G,
	input P,
	input Gprim,
	input Pprim,
	input Gprev,
	input Pprev,
	input Gprevprim,
	input Pprevprim,
	output Gout,
	output Pout,
	output Goutprim,
	output Poutprim
);

	ParallelPrefixNode normalNode(
		.G(G),
		.P(P),
		.Gprev(Gprev),
		.Pprev(Pprev),
		.Gout(Gout),
		.Pout(Pout)
	);

	ParallelPrefixNode primNode(
		.G(Gprim),
		.P(Pprim),
		.Gprev(Gprevprim),
		.Pprev(Pprevprim),
		.Gout(Goutprim),
		.Pout(Poutprim)
	);

endmodule

module SumNode(
	input H,
	input Hprim,
	input G,
	input Gprim,
	input carry,
	output S
);

	assign S = (carry == 1'b1) ? H ^ G : Hprim ^ Gprim;

endmodule

module ParallelPrefixModularAdder #(parameter N=8) (
	input [N-1:0] A,
	input [N-1:0] B,
	input [N-1:0] K,
	output [N-1:0] O
);
	parameter levels = $clog2(N);
	wire [N:0] Bprim;
	wire [N-1:-1] G[levels:0], P[levels:0], Gprim[levels:0], Pprim[levels:0];
	wire [N-1:0] H, Hprim; 
	assign O = Pprim[0][N-1:0];

	genvar i;
	genvar j;
	genvar counter;
	generate
		for(i = 0; i < levels; i = i + 1) begin
			assign G[i][-1] = 0;
			assign P[i][-1] = 0;
			assign Gprim[i][-1] = 0;
			assign Pprim[i][-1] = 0;
		end

		assign Bprim[0] = 0;
		for(i = 0; i < N; i = i + 1) begin
			PreProcessingNodeExtended pre_processing_node(
				.A(A[i]),
				.B(B[i]),
				.K(K[i]),
				.Bprim_in(Bprim[i]),
				.G(G[0][i]),
				.H(H[i]),
				.P(P[0][i]),
				.Gprim(Gprim[0][i]),
				.Hprim(Hprim[i]),
				.Pprim(Pprim[0][i]),
				.Bprim_out(Bprim[i+1])
			);
		end

		for(j = 1; j <= levels; j = j + 1) begin
			for(i = 0; i < N; i = i + 1) begin
				if(i[j] == 1'b1) begin
					ParallelPrefixNodeExtended parallel_prefix_node(
					 .G(G[j-1][i]),
					 .P(P[j-1][i]),
					 .Gprim(Gprim[j-1][i]),
					 .Pprim(Pprim[j-1][i]),
					 .Gprev(G[j-1][i-1]),
					 .Pprev(P[j-1][i-1]),
					 .Gprevprim(Gprim[j-1][i-1]),
					 .Pprevprim(Pprim[j-1][i-1]),
					 .Gout(G[j][i]),
					 .Pout(P[j][i]),
					 .Goutprim(Gprim[j][i]),
					 .Poutprim(Pprim[j][i])
					);
				end
				else begin
					assign G[j][i] = G[j-1][i];
					assign P[j][i] = P[j-1][i];
					assign Gprim[j][i] = Gprim[j-1][i];
					assign Pprim[j][i] = Pprim[j-1][i];
				end
			end
		end

	endgenerate

endmodule

module hello;
	parameter N_BIT = 7;

	reg [N_BIT - 1:0] a;
	reg [N_BIT - 1:0] b;
	reg [N_BIT - 1:0] k;
	wire [N_BIT - 1:0] sum;

	ParallelPrefixModularAdder #(N_BIT) adder_inst (
		.A(a),
		.B(b),
		.K(k),
		.O(sum)
	);

	initial begin
		a = 53;
		b = 60;
		k = 5;

		#150;

		$display("Hello world! %b", sum);
	end
endmodule



//module hello;
//	reg a;
//	reg b;
//	reg k;
//	reg bpi;
//
//	wire G, H, P, Gprim, Hprim, Pprim, Bprim_out;
//
//	PreProcessingNodeExtended p (
//		.A(a),
//		.B(b),
//		.K(k),
//		.Bprim_in(bpi),
//		.G(G),
//		.H(H),
//		.P(P),
//		.Gprim(Gprim),
//		.Hprim(Hprim),
//		.Pprim(Pprim),
//		.Bprim_out(Bprim_out)
//	);
//
//	integer counter;
//	integer n;
//
//	initial begin
//		counter = 0;
//		n = 4;
//
//		repeat(2**n) begin
//			a = counter[0];
//			b = counter[1];
//			k = counter[2];
//			bpi = counter[3];
//			#50;
//
//			$display("A: %d, B: %d, K: %d, Bprim_in: %d", a, b, k, bpi);
//			$display("G: %d, H: %d, P: %d, Gprim: %d, Hprim: %d, Pprim: %d, Bprim_out: %d", G, H, P, Gprim, Hprim, Pprim, Bprim_out);
//			$display("");
//			counter = counter + 1;
//		end
//	end
//endmodule
