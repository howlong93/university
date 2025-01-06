module SP(
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
output reg 		  [31:0] inst_addr;
output reg               mem_wen;
output reg        [11:0] mem_addr;
output reg signed [31:0] mem_din;

//------------------------------------------------------------------------
//   DECLARATION
//------------------------------------------------------------------------

// REGISTER FILE, DO NOT EDIT THE NAME.
reg	signed [31:0] r [0:31];

reg ID_valid, EX_valid, MEM_WB_valid, out_prep;

reg [31:0] IF_instruction_reg;
reg signed [31:0] IF_next_inst_addr;
reg signed [31:0] ID_next_inst_addr, EX_next_inst_addr;

wire [4:0] ID_shamt_comb;
wire [5:0] ID_funct_comb, ID_opcode_comb;
wire [4:0] ID_dest_comb;

reg [4:0] ID_shamt_reg;
reg [5:0] ID_funct_reg, ID_opcode_reg;
reg [4:0] ID_dest_reg;
reg signed [15:0] ID_imm_reg;
reg signed [31:0] ID_jump_addr, EX_jump_addr;
reg signed [31:0] ID_rs_value_reg, ID_rt_value_reg;

reg signed [31:0] ALU_result_comb, ALU_result_reg;
reg [5:0] EX_funct_reg, EX_opcode_reg;
reg [4:0] EX_dest_reg;
reg signed [15:0] EX_imm_reg;
integer i;
//------------------------------------------------------------------------
//   DESIGN
//------------------------------------------------------------------------

// IF stage
always @(negedge rst_n, posedge clk) begin
	if (~rst_n) begin
		ID_valid <= 0;
	end
	else begin
		if (in_valid) begin
			IF_next_inst_addr <= inst_addr + 4;
			IF_instruction_reg <= inst;
		end
		ID_valid <= in_valid;
	end
end

//ID stage

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

			ID_jump_addr <= {IF_next_inst_addr[31:28], IF_instruction_reg[25:0] << 2};
			ID_next_inst_addr <= IF_next_inst_addr;
		end
		EX_valid <= ID_valid;
	end
end

//EX stage
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
end

always @(*) begin
	mem_addr = ALU_result_comb;
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
			EX_jump_addr <= ID_jump_addr;

			if (ID_opcode_reg == 5) begin
				mem_wen <= 1;
			end
			else if (ID_opcode_reg == 6) begin
				mem_wen <= 0;
			end
		end
		else begin
			if (out_prep == 1)
				mem_wen <= 1;
		end
		MEM_WB_valid <= EX_valid;
	end
end

// MEM stage & write back

always @ (negedge rst_n, posedge clk) begin
	if (~rst_n) begin
		inst_addr <= 0;
		out_prep <= 0;
		for (i = 0; i < 32; i = i + 1) begin
			r[i] <= 0;
		end
	end
	else begin
		if (MEM_WB_valid) begin
			case(EX_opcode_reg)
				6'd0: begin
					if (EX_funct_reg <= 6'd6) begin
						r[EX_dest_reg] <= ALU_result_reg;
						inst_addr <= EX_next_inst_addr;
					end
					else if (EX_funct_reg ==6'd7) inst_addr <= ALU_result_reg;
					else inst_addr <= EX_next_inst_addr;
				end
				6'd1, 6'd2, 6'd3, 6'd4: begin
					r[EX_dest_reg] <= ALU_result_reg;
					inst_addr <= EX_next_inst_addr;
				end
				6'd5: begin
					r[EX_dest_reg] <= mem_dout;
					inst_addr <= EX_next_inst_addr;
				end
				6'd6: begin
					mem_din <= r[EX_dest_reg];
					inst_addr <= EX_next_inst_addr;
				end
				6'd7: begin
					if (ALU_result_reg == 0)
						inst_addr <= EX_next_inst_addr + {{14{EX_imm_reg[15]}}, EX_imm_reg[15:0], 2'b00};
					else
						inst_addr <= EX_next_inst_addr;
				end
				6'd8: begin
					if (ALU_result_reg != 0)
						inst_addr <=  EX_next_inst_addr + {{14{EX_imm_reg[15]}}, EX_imm_reg[15:0], 2'b00};
					else
						inst_addr <= EX_next_inst_addr;
				end
				6'd9: begin
					r[EX_dest_reg] <= ALU_result_reg;
					inst_addr <= EX_next_inst_addr;
				end
				6'd10: begin
					inst_addr <= EX_jump_addr;
				end
				6'd11: begin
					r[31] <= EX_next_inst_addr;
					inst_addr <= EX_jump_addr;
				end
				default: inst_addr <= EX_next_inst_addr;
			endcase
		end
		out_prep <= MEM_WB_valid;
	end
end

always @ (negedge rst_n, posedge clk) begin
	if (~rst_n) begin
		out_valid <= 0;
	end
	else out_valid <= out_prep;
end

endmodule
