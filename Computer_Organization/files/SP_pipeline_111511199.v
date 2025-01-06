module SP_pipeline(
	// INPUT SIGNAL
	clk,
	rst_n,
	in_valid,
	inst,
	mem_dout,
	// OUTPUT SIGNAL
	out_valid,
	inst_addr,
	mem_wen,
	mem_addr,
	mem_din
);

//------------------------------------------------------------------------
//   INPUT AND OUTPUT DECLARATION                         
//------------------------------------------------------------------------

input                    clk, rst_n, in_valid;
input             [31:0] inst;
input  signed     [31:0] mem_dout;
output reg               out_valid;
output reg        [31:0] inst_addr;
output reg               mem_wen;
output reg        [11:0] mem_addr;
output reg signed [31:0] mem_din;

//------------------------------------------------------------------------
//   DECLARATION
//------------------------------------------------------------------------

// REGISTER FILE, DO NOT EDIT THE NAME.
reg	signed [31:0] r [0:31]; 
reg ID_valid, EX_valid, MEM_WB_valid, out_prep;

wire [5:0] IF_opcode_comb, IF_funct_comb;
wire [4:0] IF_rs, IF_rt;

reg [31:0] IF_instruction_reg;
reg [31:0] IF_next_inst_addr;
reg [31:0] ID_next_inst_addr, EX_next_inst_addr;

wire [4:0] ID_shamt_comb;
wire [5:0] ID_funct_comb, ID_opcode_comb;
wire [4:0] ID_dest_comb;
reg [11:0] mem_addr_comb;

reg [4:0] ID_shamt_reg;
reg [5:0] ID_funct_reg, ID_opcode_reg;
reg [4:0] ID_dest_reg;
reg signed [15:0] ID_imm_reg;
reg signed [31:0] ID_rs_value_reg, ID_rt_value_reg;

//reg signed [31:0] ALU_result_comb, ALU_result_reg;
integer ALU_result_comb, ALU_result_reg;
reg [5:0] EX_funct_reg, EX_opcode_reg;
reg [4:0] EX_dest_reg;
reg signed [15:0] EX_imm_reg;

//------------------------------------------------------------------------
//   DESIGN
//------------------------------------------------------------------------

assign IF_funct_comb = inst[5:0];
assign IF_opcode_comb = inst[31:26];
assign IF_rs = inst[25:21];
assign IF_rt = inst[20:16];

// 1: IF stage
always @(negedge rst_n, posedge clk) begin
	if (~rst_n) begin
		ID_valid <= 0;
		inst_addr <= 0;
	end
	else begin
		if (in_valid) begin
			IF_next_inst_addr <= inst_addr + 4;
			IF_instruction_reg <= inst;

			if (IF_opcode_comb == 0 && IF_funct_comb == 7)
				inst_addr <= r[IF_rs];
			else if (IF_opcode_comb == 'h07 && (r[IF_rs] == r[IF_rt]))
				inst_addr <= inst_addr + 4 + {{14{inst[15]}}, inst[15:0], 2'b00};
			else if (IF_opcode_comb == 'h08 && (r[IF_rs] != r[IF_rt]))
				inst_addr <= inst_addr + 4 + {{14{inst[15]}}, inst[15:0], 2'b00};
			else if (IF_opcode_comb >= 'h0a)
				inst_addr <= {inst_addr[31:28], inst[25:0], 2'b00};
			else
				inst_addr <= inst_addr + 'd4;
		end
		ID_valid <= in_valid;
	end
end

// 2: ID stage

assign ID_shamt_comb = IF_instruction_reg[10:6];
assign ID_funct_comb = IF_instruction_reg[5:0];
assign ID_opcode_comb = IF_instruction_reg[31:26];
assign ID_dest_comb = (IF_instruction_reg[31:26] == 0) ? IF_instruction_reg[15:11] : IF_instruction_reg[20:16];

always @(negedge rst_n, posedge clk) begin
	if (~rst_n) begin
		EX_valid <= 0;
	end
	else begin
		if (ID_valid) begin
			ID_opcode_reg <= ID_opcode_comb;
			ID_funct_reg <= ID_funct_comb;
			ID_shamt_reg <= ID_shamt_comb;
			ID_imm_reg <= IF_instruction_reg[15:0];

			ID_rs_value_reg <= r[IF_instruction_reg[25:21]];
			ID_rt_value_reg <= r[IF_instruction_reg[20:16]];

			ID_dest_reg <= ID_dest_comb;

			ID_next_inst_addr <= IF_next_inst_addr;
		end
		EX_valid <= ID_valid;
	end
end

// 3: EX stage
always @(*) begin //ALU operations: combinational
	case (ID_opcode_reg)
		6'd0:
			case (ID_funct_reg)
				6'd0: ALU_result_comb = ID_rs_value_reg & ID_rt_value_reg;
				6'd1: ALU_result_comb = ID_rs_value_reg | ID_rt_value_reg;
				6'd2: ALU_result_comb = ID_rs_value_reg + ID_rt_value_reg;
				6'd3: ALU_result_comb = ID_rs_value_reg - ID_rt_value_reg;
				6'd4: begin
					if (ID_rs_value_reg < ID_rt_value_reg)
						ALU_result_comb = 32'd1;
					else
						ALU_result_comb = 32'd0;
				end
				6'd5: ALU_result_comb = ID_rs_value_reg << ID_shamt_reg;
				6'd6: ALU_result_comb = ~(ID_rs_value_reg | ID_rt_value_reg);
				6'd7: ALU_result_comb = ID_rs_value_reg;
				default: ALU_result_comb = 0;
			endcase
		6'd1: ALU_result_comb = ID_rs_value_reg & {16'd0, ID_imm_reg};
		6'd2: ALU_result_comb = ID_rs_value_reg | {16'd0, ID_imm_reg};
		6'd3: ALU_result_comb = ID_rs_value_reg + {{16{ID_imm_reg[15]}}, ID_imm_reg};
		6'd4: ALU_result_comb = ID_rs_value_reg - {{16{ID_imm_reg[15]}}, ID_imm_reg};
		6'd5: ALU_result_comb = ID_rs_value_reg + {{16{ID_imm_reg[15]}}, ID_imm_reg};
		6'd6: ALU_result_comb = ID_rs_value_reg + {{16{ID_imm_reg[15]}}, ID_imm_reg};
		6'd7: ALU_result_comb = ID_rs_value_reg - ID_rt_value_reg;
		6'd8: ALU_result_comb = ID_rs_value_reg - ID_rt_value_reg;
		6'd9: ALU_result_comb = {ID_imm_reg, 16'd0};
		default: ALU_result_comb = 0;
	endcase
	if (ID_opcode_reg == 5 || ID_opcode_reg == 6) begin
		mem_addr = ALU_result_comb;
		mem_wen = (ID_opcode_reg == 6) ? 0 : 1;
		mem_din = r[ID_dest_reg];
	end
	else begin
		mem_addr = 0;
		mem_wen = 1;
		mem_din = 0;
	end
end

always @(negedge rst_n, posedge clk) begin
	if (~rst_n) begin
		MEM_WB_valid <= 0;
		mem_wen <= 1;
	end
	else begin
		if (EX_valid) begin
			ALU_result_reg <= ALU_result_comb;
			EX_dest_reg <= ID_dest_reg;
			EX_opcode_reg <= ID_opcode_reg;
			EX_funct_reg <= ID_funct_reg;
			EX_next_inst_addr <= ID_next_inst_addr;
			EX_imm_reg <= ID_imm_reg;
		end

		MEM_WB_valid <= EX_valid;
	end
end

// 4: MEM stage & write back
integer i, pattern_cnt;
always @ (negedge rst_n, posedge clk) begin
	if (~rst_n) begin
		out_valid <= 0;
		for (i = 0; i < 32; i = i + 1) begin
			r[i] <= 0;
		end
		pattern_cnt <= 0;
	end
	else begin
		if (MEM_WB_valid) begin
			pattern_cnt <= pattern_cnt + 1;
			case(EX_opcode_reg)
				6'd0: begin
					if (EX_funct_reg <= 6'd6) begin
						r[EX_dest_reg] <= ALU_result_reg;
					end
				end
				6'd1, 6'd2, 6'd3, 6'd4: begin
					r[EX_dest_reg] <= ALU_result_reg;
				end
				6'd5: begin
					r[EX_dest_reg] <= mem_dout;
				end
				6'd6: begin
				end
				6'd9: begin
					r[EX_dest_reg] <= ALU_result_reg;
				end
				6'd11: begin
					r[31] <= EX_next_inst_addr;
				end
			endcase
		end
		out_valid <= MEM_WB_valid;
	end
end

// 5: output valid
// always @ (negedge rst_n, posedge clk) begin
// 	if (~rst_n) begin
// 		out_valid <= 0;
// 	end
// 	else out_valid <= out_prep;
// end

endmodule