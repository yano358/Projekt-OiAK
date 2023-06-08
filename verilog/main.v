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

	assign S = (carry == 1'b0) ? H ^ G : Hprim ^ Gprim;

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

	genvar i;
	genvar j;
	genvar counter;
	generate
		for(i = 0; i <= levels; i = i + 1) begin
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
				if(i[j-1] == 1'b1) begin
					localparam PREVIOUS = i - (i % (2**(j-1)) + 1);
					ParallelPrefixNodeExtended parallel_prefix_node(
					 .G(G[j-1][i]),
					 .P(P[j-1][i]),
					 .Gprim(Gprim[j-1][i]),
					 .Pprim(Pprim[j-1][i]),
					 .Gprev(G[j-1][PREVIOUS]),
					 .Pprev(P[j-1][PREVIOUS]),
					 .Gprevprim(Gprim[j-1][PREVIOUS]),
					 .Pprevprim(Pprim[j-1][PREVIOUS]),
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

		for (i = 0; i < N; i = i+1) begin
			SumNode sum_node(
				.H(H[i]),
				.Hprim(Hprim[i]),
				.G(G[levels][i-1]),
				.Gprim(Gprim[levels][i-1]),
				.carry(G[levels][N-1] | Gprim[levels][N-1]),
				.S(O[i])
			);
		end
	endgenerate
endmodule

module hello;
	parameter N_BIT = 7;

	reg [N_BIT - 1:0] a;
	reg [N_BIT - 1:0] b;
	reg [N_BIT - 1:0] k;
	reg [N_BIT - 1:0] expected;
	wire [N_BIT - 1:0] sum;
	reg done;

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
		done = 0;
		for(k = 3; k < 2**(N_BIT-1); k = k + 1) begin
			for(a = 0; a < 2**N_BIT-k; a=a+1) begin
				for(b = 0; b < 2**N_BIT-k; b=b+1) begin
					if(done == 0) begin
						expected = (a + b) % (2**N_BIT-k);
						#10;
						$display("Expected: %d, Actual: %d, A: %d, B: %d, K: %d", expected, sum, a, b, k);
						if(expected != sum) begin
							done = 1;
						end
					end
				end
			end
		end
		#150;
	end
endmodule

